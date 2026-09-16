#!/usr/bin/env python3
"""Resolve where a file the plugin produces goes: `<outputs_dir>/<ext>/<name> YYYYMMDD HHMM.<ext>`.

Plugin-root script owned by no skill (1.22.0). Every skill, agent and `office_kopru.py`
takes an output path from here instead of composing one — the layout rule lives in one place:

- one subfolder per **extension** (`pptx/`, `docx/`, `pdf/`, `md/`, `png/`, `jpg/`, `js/`, …),
  created on demand; nothing is ever written to the `outputs_dir` root itself;
- the **job-start stamp** `YYYYMMDD HHMM` (local time) at the end of the name, so every file
  of one run carries the same stamp and a later run never overwrites an earlier one;
- version suffixes are gone: `_v2`, a previous stamp, a doubled `_zref` are stripped from the
  name (`sade_ad`) — the stamp is the version;
- a name+stamp already on disk gets ` -2`, ` -3`, … (never an overwrite);
- `paket=True` returns a **folder** of that name (the poster pipeline keeps manifest, assets
  and audits in one package because its asset check refuses paths outside the manifest dir);
- **backups (1.23.0):** when a new file is resolved into an extension folder, every entry of
  that folder that does not belong to the current job moves to `<ext>/yedekler/` (`yedekle`):
  an entry whose stamp is **older** than the job stamp, or that carries **no** valid stamp,
  moves; an entry with the **same** stamp (siblings of one run: `-grid-1`, ` -2`, slide PNGs,
  a poster package) or a **newer** one stays. Nothing is deleted or overwritten — a name
  already in `yedekler/` gets ` -2`; a locked file (open in PowerPoint/Word) is skipped and
  reported, and the next resolve retries it. Only the folder receiving the new file is swept.
  A file the job is about to READ from that folder (a deck being edited, a docx being cited)
  is passed as `--kaynak`: it stays for this run (`yedek_ertelenen`) and moves on the next.

Usage (CLI, one JSON on stdout, exit 0 / 2):
    python cikti_yolcoz.py --outputs-dir DIR --ad NAME --uzanti EXT [--damga "YYYYMMDD HHMM"]
                           [--ek SUFFIX] [--paket] [--kaynak SOURCE ...]
    → {"path", "klasor", "ad", "damga", "paket", "yedeklenen", "yedek_atlanan", "yedek_ertelenen"}
    python cikti_yolcoz.py --supur OUTPUTS_DIR [--kuru]
    → {"outputs_dir", "kuru", "klasorler": {ext: {"guncel_damga", "tasinan", "atlanan"}}}
      (one-off / manual sweep: each extension folder keeps its newest stamp)

Library:
    from cikti_yolcoz import damga, sade_ad, yol, yedekle, damga_bul
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

STAMP_RE = re.compile(r"^\d{8} \d{4}$")
_STAMP_ANY_RE = re.compile(r"(?<!\d)(\d{8} \d{4})(?!\d)")
YEDEK_KLASORU = "yedekler"
# trailing "<stamp>", "<stamp> -N" or "_vN" — stripped repeatedly until nothing matches
_TAIL_RE = re.compile(r"(?: \d{8} \d{4}(?: -\d+)?|_v\d+)$")
_DOUBLE_ZREF_RE = re.compile(r"(_zref)(?:_zref)+$")


def damga(now=None):
    """Job-start stamp: local `YYYYMMDD HHMM`."""
    return (now or datetime.now()).strftime("%Y%m%d %H%M")


def sade_ad(ad):
    """Bare name: no extension, no old stamp, no `_vN`, no doubled `_zref`.

    A stamp that is NOT at the very end (`1 tez c2 20260907 0740 isaretli`) is part of the
    name and stays — only the tail is the layout's own suffix.
    """
    ad = ad.strip()
    root, ext = os.path.splitext(ad)
    if ext and len(ext) <= 6 and ext[1:].isalnum():
        ad = root
    while True:
        yeni = _TAIL_RE.sub("", ad)
        yeni = _DOUBLE_ZREF_RE.sub(r"\1", yeni)
        if yeni == ad:
            return ad.strip()
        ad = yeni


def damga_bul(ad):
    """Last valid `YYYYMMDD HHMM` in a name, else None (`13092026 2306` is not a date).

    Last, not first: a user name that already carries a stamp (`1 tez c2 20260907 0740
    isaretli`) gets the layout stamp appended after it, and that one is the version.
    """
    for m in reversed(list(_STAMP_ANY_RE.finditer(ad))):
        try:
            datetime.strptime(m.group(1), "%Y%m%d %H%M")
        except ValueError:
            continue
        return m.group(1)
    return None


def _bos_hedef(klasor, ad):
    """`ad` inside `klasor`, with ` -2`, ` -3`, … before the extension when already taken."""
    hedef = os.path.join(klasor, ad)
    if not os.path.exists(hedef):
        return hedef
    root, ext = os.path.splitext(ad)
    if os.path.isdir(os.path.join(klasor, ad)) or not (ext and len(ext) <= 6 and ext[1:].isalnum()):
        root, ext = ad, ""
    n = 2
    while True:
        hedef = os.path.join(klasor, f"{root} -{n}{ext}")
        if not os.path.exists(hedef):
            return hedef
        n += 1


def yedekle(klasor, damga_str, kuru=False, haric=()):
    """Move every entry of an extension folder that is not the current job's into `yedekler/`.

    Moves: stamp older than `damga_str`, or no valid stamp. Keeps: same or newer stamp, the
    `yedekler/` folder itself, Office owner files (`~$…`), and every path in `haric` (the job's own source files — they
    move on the next sweep). `kuru=True` only lists. Returns {"tasinan": [[src, dst], …],
    "atlanan": [{"path", "neden"}, …], "ertelenen": [path, …]} — a locked file is skipped.
    """
    if not STAMP_RE.match(damga_str or ""):
        raise ValueError(f"bad stamp: {damga_str!r} (expected 'YYYYMMDD HHMM')")
    sonuc = {"tasinan": [], "atlanan": [], "ertelenen": []}
    klasor = os.path.abspath(klasor)
    muaf = {os.path.normcase(os.path.abspath(h)) for h in haric if h}
    if not os.path.isdir(klasor):
        return sonuc
    yedek_dir = os.path.join(klasor, YEDEK_KLASORU)
    for ad in sorted(os.listdir(klasor)):
        # `~$x.pptx` is Office's owner file for an open document; moving it breaks the session
        if ad == YEDEK_KLASORU or ad.startswith("~$"):
            continue
        d = damga_bul(ad)
        # "YYYYMMDD HHMM" compares correctly as a string
        if d is not None and d >= damga_str:
            continue
        src = os.path.join(klasor, ad)
        if os.path.normcase(src) in muaf:
            sonuc["ertelenen"].append(src)
            continue
        if kuru:
            sonuc["tasinan"].append([src, os.path.join(yedek_dir, ad)])
            continue
        try:
            os.makedirs(yedek_dir, exist_ok=True)
            dst = _bos_hedef(yedek_dir, ad)
            os.rename(src, dst)
            sonuc["tasinan"].append([src, dst])
        except OSError as exc:
            sonuc["atlanan"].append({"path": src, "neden": f"{type(exc).__name__}: {exc.strerror or exc}"})
    return sonuc


def supur(outputs_dir, kuru=False):
    """Sweep every extension folder of `outputs_dir`: each keeps its own newest stamp."""
    outputs_dir = os.path.abspath(outputs_dir)
    klasorler = {}
    for u in sorted(os.listdir(outputs_dir)):
        klasor = os.path.join(outputs_dir, u)
        if not os.path.isdir(klasor) or u.startswith("."):
            continue
        damgalar = [d for d in (damga_bul(a) for a in os.listdir(klasor)
                                if a != YEDEK_KLASORU and not a.startswith("~$")) if d]
        if not damgalar:
            klasorler[u] = {"guncel_damga": None, "tasinan": [], "atlanan": [], "ertelenen": [],
                            "not": "no stamped entry - nothing to compare against, left as is"}
            continue
        guncel = max(damgalar)
        klasorler[u] = {"guncel_damga": guncel, **yedekle(klasor, guncel, kuru=kuru)}
    return {"outputs_dir": outputs_dir, "kuru": kuru, "klasorler": klasorler}


def _uzanti(uzanti):
    u = uzanti.strip().lstrip(".").lower()
    if not u or not u.isalnum():
        raise ValueError(f"bad extension: {uzanti!r}")
    return u


def yol(outputs_dir, ad, uzanti, damga_str, ek="", paket=False, yedek=True, haric=()):
    """Absolute destination path; the extension folder is created, the file is not.

    `ek` is a suffix glued to the bare name before the stamp (`_zref`, `_poster`, `-grid`).
    `paket=True` returns (and creates) a folder `<ext>/<name><ek> <stamp>` instead of a file.
    `yedek=True` first moves the folder's older entries to `yedekler/` (`yedekle`), except
    the paths in `haric`.
    """
    if not STAMP_RE.match(damga_str or ""):
        raise ValueError(f"bad stamp: {damga_str!r} (expected 'YYYYMMDD HHMM')")
    u = _uzanti(uzanti)
    klasor = os.path.join(os.path.abspath(outputs_dir), u)
    os.makedirs(klasor, exist_ok=True)
    if yedek:
        yedekle(klasor, damga_str, haric=haric)
    govde = f"{sade_ad(ad)}{ek} {damga_str}"
    n = 1
    while True:
        aday = govde if n == 1 else f"{govde} -{n}"
        target = os.path.join(klasor, aday if paket else f"{aday}.{u}")
        if not os.path.exists(target):
            break
        n += 1
    if paket:
        os.makedirs(target, exist_ok=True)
    return target


def main(argv=None):
    ap = argparse.ArgumentParser(description="plugin-journal output path resolver")
    ap.add_argument("--supur", metavar="OUTPUTS_DIR", default=None,
                    help="sweep every extension folder (each keeps its newest stamp) and exit")
    ap.add_argument("--kuru", action="store_true", help="with --supur: list only, move nothing")
    ap.add_argument("--outputs-dir", help="the workspace's outputs_dir")
    ap.add_argument("--ad", help="base name (old stamp/_vN/extension are stripped)")
    ap.add_argument("--uzanti", help="extension = subfolder (pptx, docx, md, png …)")
    ap.add_argument("--damga", default=None, help="job-start stamp 'YYYYMMDD HHMM' (default: now)")
    ap.add_argument("--ek", default="", help="suffix before the stamp (_zref, _poster, -grid)")
    ap.add_argument("--paket", action="store_true", help="return a package FOLDER, not a file")
    ap.add_argument("--kaynak", action="append", default=[],
                    help="a file this job reads from the target folder: not moved this run (repeatable)")
    a = ap.parse_args(argv)
    if a.supur:
        if not os.path.isdir(a.supur):
            print(json.dumps({"error": "no_outputs_dir", "message": a.supur}, ensure_ascii=False))
            return 2
        print(json.dumps(supur(a.supur, kuru=a.kuru), ensure_ascii=False, indent=1))
        return 0
    if not (a.outputs_dir and a.ad and a.uzanti):
        ap.error("--outputs-dir, --ad and --uzanti are required (or --supur)")
    stamp = a.damga or damga()
    try:
        u = _uzanti(a.uzanti)
        y = yedekle(os.path.join(os.path.abspath(a.outputs_dir), u), stamp, haric=a.kaynak)
        p = yol(a.outputs_dir, a.ad, u, stamp, ek=a.ek, paket=a.paket, yedek=False)
    except ValueError as exc:
        code = "bad_stamp" if "stamp" in str(exc) else "bad_extension"
        print(json.dumps({"error": code, "message": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"path": p, "klasor": os.path.dirname(p), "ad": os.path.basename(p),
                      "damga": stamp, "paket": a.paket,
                      "yedeklenen": [dst for _, dst in y["tasinan"]],
                      "yedek_atlanan": y["atlanan"], "yedek_ertelenen": y["ertelenen"]},
                     ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
