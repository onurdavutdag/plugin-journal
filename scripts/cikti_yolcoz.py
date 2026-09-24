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
- **backups (1.23.0, scoped to one document since 1.24.0):** when a new file is resolved into
  an extension folder, the earlier versions **of the same document** move to `<ext>/yedekler/`
  (`yedekle`). Same document = same key (`belge_anahtari`): the name without extension, without
  a side suffix (`-s01`, `-grid-2`, `_handoff_modal-1`, ` -2`) and without its trailing stamp;
  the job's key is `sade_ad(ad) + ek`, and a `_zref` / `_zref_updated` suffix is NOT part of
  the key (`anahtar_normalle`): the marker source, its render and Word's refreshed copy are one
  document, so a newer render also moves the older source (user rule, 2026-09-24). Other
  suffixes (`_poster`, `_sunum`, `_<slug>`, `_original_backup`) remain separate documents, and so
  does a different `--ad` — one document, one `--ad`; the stamp is the version. A user's
  one-word descriptor AFTER the stamp (`1 tez c2 20260907 0740 isaretli`) qualifies that version
  and keeps the key (user rule, 2026-09-24); ` - Kopya`, ` (2)` or a multi-word tail is still a
  separate, stampless entry no job moves. Of the entries with that key, one whose stamp is
  **older** than the job stamp, or not a valid date (`13092026 2306`), moves; the **same**
  stamp (one run's siblings) or a **newer** one stays. Every entry with another key stays —
  updating deck A never pushes deck B away (user rule, 2026-09-16). Nothing is deleted or
  overwritten — a name already in `yedekler/` gets ` -2`; a locked file (open in
  PowerPoint/Word) is skipped and reported, and the next resolve retries it. Only the folder
  receiving the new file is swept. A file the job is about to READ from that folder (a deck
  being edited, a docx being cited) is passed as `--kaynak`: it stays for this run
  (`yedek_ertelenen`) and moves on the next. **Inside `yedekler/` every document has its own
  subfolder** named after its key (`docx/yedekler/1 tez c2/…`; user rule 2026-09-24,
  `yedek_alt_klasor`); `--supur` also files legacy flat backups into their subfolder
  (`duzenlenen`) and `--geri-al` reads both layouts.

Usage (CLI, one JSON on stdout, exit 0 / 2):
    python cikti_yolcoz.py --outputs-dir DIR --ad NAME --uzanti EXT [--damga "YYYYMMDD HHMM"]
                           [--ek SUFFIX] [--paket] [--kaynak SOURCE ...]
    → {"path", "klasor", "ad", "damga", "paket", "yedeklenen", "yedek_atlanan", "yedek_ertelenen"}
    python cikti_yolcoz.py --supur OUTPUTS_DIR [--kuru]
    → {"outputs_dir", "kuru", "klasorler": {ext: {"tasinan", "atlanan", "ertelenen", "gruplar"}}}
      (manual sweep: every document key keeps its own newest stamp)
    python cikti_yolcoz.py --geri-al OUTPUTS_DIR [--kuru]
    → {"outputs_dir", "kuru", "klasorler": {ext: {"geri_alinan", "atlanan"}}}
      (1.24.0 repair: a document whose newest version sits only in `yedekler/` gets that
      version — with its same-stamp siblings — back into the extension folder)

Library:
    from cikti_yolcoz import damga, sade_ad, yol, yedekle, damga_bul, belge_anahtari
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
# the zotero render chain is one document: `<ad>`, `<ad>_zref`, `<ad>_zref_updated` share a key
# (user rule, 2026-09-24: a new render moves the marker source to yedekler/ too)
_ZREF_EK_RE = re.compile(r"_zref(?:_updated)?$", re.IGNORECASE)
# side suffixes a run glues AFTER the stamp: slide PNGs, grid sheets, modal captures, collisions
_SIDE_RE = re.compile(r"(?:-s\d{2,3}|-grid(?:-\d+)?|_handoff_modal-\d+|_modal-\d+| -\d+)$")
_TAIL_STAMP_RE = re.compile(r"^(.*?)[ _-]?(?<!\d)(\d{8} \d{4})$")
# "<stamp> <one word>" — a user's one-word descriptor after the stamp (`isaretli`, `temiz`) names a
# VERSION of the same document (user rule, 2026-09-24); ` - Kopya`, ` (2)` and multi-word tails
# stay their own documents (no stamp, never moved)
_TAIL_STAMP_DESC_RE = re.compile(r"^(.*?)[ _-]?(?<!\d)(\d{8} \d{4}) ([^\s\-()]+)$")


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


def _gecerli(d):
    try:
        datetime.strptime(d, "%Y%m%d %H%M")
        return True
    except ValueError:
        return False


def anahtar_normalle(anahtar):
    """Document key without the zotero render suffix: `X_zref` / `X_zref_updated` → `X`.

    The marker source, its render and Word's refreshed copy are versions of ONE document, so a
    newer render moves the older source as well (user rule, 2026-09-24). Other suffixes
    (`_poster`, `_sunum`, `_<slug>`, `_original_backup`) stay — those are separate documents.
    """
    a = _DOUBLE_ZREF_RE.sub(r"\1", anahtar.strip())
    return _ZREF_EK_RE.sub("", a).strip()


def belge_anahtari(ad, klasor_mu=False):
    """(key, stamp|None) of an output entry — which document it is a version of.

    `Davut Presentation 20260916 2239-s01.png` → ("Davut Presentation", "20260916 2239");
    `Davut Presentation 13092026 2306.pptx` → ("Davut Presentation", None) — stamp-shaped but
    not a date, so it counts as older than any job; `vaka1_sunum 20260913 0540 - Kopya.pptx` →
    (the whole name, None) — a user copy no job's key matches;
    `makale_zref 20260924 1924.docx` → ("makale", "20260924 1924") — same document as `makale`;
    `1 tez c2 20260907 0740 isaretli.docx` → ("1 tez c2", "20260907 0740") — a one-word
    descriptor after the stamp qualifies the version, it does not start a new document.
    """
    govde = ad.strip()
    if not klasor_mu:
        root, ext = os.path.splitext(govde)
        if ext and len(ext) <= 6 and ext[1:].isalnum():
            govde = root
    while True:
        yeni = _SIDE_RE.sub("", govde)
        if yeni == govde:
            break
        govde = yeni
        if _TAIL_STAMP_RE.match(govde):
            break
    m = _TAIL_STAMP_RE.match(govde) or _TAIL_STAMP_DESC_RE.match(govde)
    if m and m.group(1).strip():
        return anahtar_normalle(m.group(1)), (m.group(2) if _gecerli(m.group(2)) else None)
    return anahtar_normalle(govde if klasor_mu else sade_ad(govde)), None


def _ayni_anahtar(a, b):
    return a.casefold() == b.casefold()


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


def yedekle(klasor, damga_str, anahtar, kuru=False, haric=()):
    """Move the earlier versions of ONE document in an extension folder into `yedekler/`.

    Only entries whose `belge_anahtari` key equals `anahtar` (case-insensitive) are considered;
    every other document stays where it is. Of those, moves: stamp older than `damga_str`, or
    no valid stamp. Keeps: same or newer stamp, the `yedekler/` folder itself, Office owner files
    (`~$…`), and every path in `haric` (the job's own source files — they move on the next
    sweep). `kuru=True` only lists. Returns {"tasinan": [[src, dst], …],
    "atlanan": [{"path", "neden"}, …], "ertelenen": [path, …]} — a locked file is skipped.
    """
    if not STAMP_RE.match(damga_str or ""):
        raise ValueError(f"bad stamp: {damga_str!r} (expected 'YYYYMMDD HHMM')")
    if not (anahtar or "").strip():
        raise ValueError("empty document key: yedekle needs the job's name")
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
        src = os.path.join(klasor, ad)
        k, d = belge_anahtari(ad, klasor_mu=os.path.isdir(src))
        if not _ayni_anahtar(k, anahtar.strip()):
            continue
        # "YYYYMMDD HHMM" compares correctly as a string
        if d is not None and d >= damga_str:
            continue
        if os.path.normcase(src) in muaf:
            sonuc["ertelenen"].append(src)
            continue
        # one subfolder per document inside yedekler/ (user rule, 2026-09-24)
        hedef_dir = os.path.join(yedek_dir, yedek_alt_klasor(k))
        if kuru:
            sonuc["tasinan"].append([src, os.path.join(hedef_dir, ad)])
            continue
        try:
            os.makedirs(hedef_dir, exist_ok=True)
            dst = _bos_hedef(hedef_dir, ad)
            os.rename(src, dst)
            sonuc["tasinan"].append([src, dst])
        except OSError as exc:
            sonuc["atlanan"].append({"path": src, "neden": f"{type(exc).__name__}: {exc.strerror or exc}"})
    return sonuc


def yedek_alt_klasor(anahtar):
    """Folder name for a document inside `yedekler/`: its key, trimmed of trailing dots/spaces
    (Windows drops them) — a key never contains a path separator, it comes from a file name."""
    a = (anahtar or "").strip().rstrip(". ")
    return a or "_adsiz"


def _yedek_girdileri(yedek_dir):
    """[(dir, name)] of every backup entry: files in the per-document subfolders and — for
    backups written before 2026-09-24 — flat files directly under `yedekler/`."""
    girdiler = []
    if not os.path.isdir(yedek_dir):
        return girdiler
    for a in sorted(os.listdir(yedek_dir)):
        if a.startswith("~$"):
            continue
        p = os.path.join(yedek_dir, a)
        # a per-document folder carries no stamp; a legacy flat entry (file, or a stamped
        # poster package folder) sits directly here
        if os.path.isdir(p) and belge_anahtari(a, klasor_mu=True)[1] is None:
            for b in sorted(os.listdir(p)):
                if not b.startswith("~$"):
                    girdiler.append((p, b))
        else:
            girdiler.append((yedek_dir, a))
    return girdiler


def yedek_duzenle(yedek_dir, kuru=False):
    """Move legacy flat entries of `yedekler/` into their per-document subfolder."""
    rapor = {"duzenlenen": [], "atlanan": []}
    for d, a in _yedek_girdileri(yedek_dir):
        if d != yedek_dir:
            continue
        src = os.path.join(d, a)
        k, _ = belge_anahtari(a, klasor_mu=os.path.isdir(src))
        hedef_dir = os.path.join(yedek_dir, yedek_alt_klasor(k))
        if os.path.normcase(hedef_dir) == os.path.normcase(src):
            continue
        if kuru:
            rapor["duzenlenen"].append([src, os.path.join(hedef_dir, a)])
            continue
        try:
            os.makedirs(hedef_dir, exist_ok=True)
            dst = _bos_hedef(hedef_dir, a)
            os.rename(src, dst)
            rapor["duzenlenen"].append([src, dst])
        except OSError as exc:
            rapor["atlanan"].append({"path": src, "neden": f"{type(exc).__name__}: {exc.strerror or exc}"})
    return rapor


def _gruplar(adlar, klasor):
    """{key.casefold(): {"anahtar", "damgalar": set}} over entry names of `klasor`."""
    g = {}
    for a in adlar:
        if a == YEDEK_KLASORU or a.startswith("~$"):
            continue
        k, d = belge_anahtari(a, klasor_mu=os.path.isdir(os.path.join(klasor, a)))
        e = g.setdefault(k.casefold(), {"anahtar": k, "damgalar": set()})
        if d:
            e["damgalar"].add(d)
    return g


def supur(outputs_dir, kuru=False):
    """Sweep every extension folder of `outputs_dir`: each document keeps its own newest stamp."""
    outputs_dir = os.path.abspath(outputs_dir)
    klasorler = {}
    for u in sorted(os.listdir(outputs_dir)):
        klasor = os.path.join(outputs_dir, u)
        if not os.path.isdir(klasor) or u.startswith("."):
            continue
        rapor = {"tasinan": [], "atlanan": [], "ertelenen": [], "gruplar": {}}
        for e in _gruplar(os.listdir(klasor), klasor).values():
            if not e["damgalar"]:
                continue  # no valid stamp in the group: nothing to compare against, left as is
            guncel = max(e["damgalar"])
            rapor["gruplar"][e["anahtar"]] = guncel
            r = yedekle(klasor, guncel, e["anahtar"], kuru=kuru)
            for alan in ("tasinan", "atlanan", "ertelenen"):
                rapor[alan].extend(r[alan])
        # legacy flat backups → one subfolder per document (2026-09-24)
        d = yedek_duzenle(os.path.join(klasor, YEDEK_KLASORU), kuru=kuru)
        rapor["duzenlenen"] = d["duzenlenen"]
        rapor["atlanan"].extend(d["atlanan"])
        klasorler[u] = rapor
    return {"outputs_dir": outputs_dir, "kuru": kuru, "klasorler": klasorler}


def geri_al(outputs_dir, kuru=False):
    """1.24.0 repair: bring back each document's newest version that sits only in `yedekler/`.

    Per extension folder, entries of the folder and of its `yedekler/` are grouped by document
    key. When the newest valid stamp of a group is present only in `yedekler/`, every backup
    entry of that group with that stamp (its run siblings) moves back; a group with no valid
    stamp anywhere and no member in the folder gets its backup members back (a user copy the
    old folder-wide rule swept). A name already present in the folder is skipped, never
    overwritten.
    """
    outputs_dir = os.path.abspath(outputs_dir)
    klasorler = {}
    for u in sorted(os.listdir(outputs_dir)):
        klasor = os.path.join(outputs_dir, u)
        yedek_dir = os.path.join(klasor, YEDEK_KLASORU)
        if not os.path.isdir(yedek_dir) or u.startswith("."):
            continue
        yerinde = _gruplar(os.listdir(klasor), klasor)
        rapor = {"geri_alinan": [], "atlanan": []}
        # per-document subfolders (2026-09-24) and legacy flat entries alike
        girdiler = _yedek_girdileri(yedek_dir)
        yedekte = {}
        for gd, a in girdiler:
            k, d = belge_anahtari(a, klasor_mu=os.path.isdir(os.path.join(gd, a)))
            e = yedekte.setdefault(k.casefold(), {"anahtar": k, "damgalar": set()})
            if d:
                e["damgalar"].add(d)
        for anahtar_cf, e in yedekte.items():
            burada = yerinde.get(anahtar_cf)
            tum = set(e["damgalar"]) | (burada["damgalar"] if burada else set())
            if tum:
                en_yeni = max(tum)
                if burada and en_yeni in burada["damgalar"]:
                    continue
                if en_yeni not in e["damgalar"]:
                    continue
                secilen = lambda d, _y=en_yeni: d == _y  # noqa: E731
            else:
                if burada:
                    continue
                secilen = lambda d: d is None  # noqa: E731
            for gd, a in girdiler:
                src = os.path.join(gd, a)
                k, d = belge_anahtari(a, klasor_mu=os.path.isdir(src))
                if k.casefold() != anahtar_cf or not secilen(d):
                    continue
                dst = os.path.join(klasor, a)
                if os.path.exists(dst):
                    rapor["atlanan"].append({"path": src, "neden": "name already in folder"})
                    continue
                if not kuru:
                    try:
                        os.rename(src, dst)
                    except OSError as exc:
                        rapor["atlanan"].append({"path": src, "neden": f"{type(exc).__name__}: {exc.strerror or exc}"})
                        continue
                rapor["geri_alinan"].append([src, dst])
        klasorler[u] = rapor
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
    `yedek=True` first moves this document's older versions to `yedekler/` (`yedekle`), except
    the paths in `haric`.
    """
    if not STAMP_RE.match(damga_str or ""):
        raise ValueError(f"bad stamp: {damga_str!r} (expected 'YYYYMMDD HHMM')")
    u = _uzanti(uzanti)
    klasor = os.path.join(os.path.abspath(outputs_dir), u)
    os.makedirs(klasor, exist_ok=True)
    if yedek:
        yedekle(klasor, damga_str, anahtar_normalle(f"{sade_ad(ad)}{ek}"), haric=haric)
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
                    help="sweep every extension folder (each document keeps its newest stamp) and exit")
    ap.add_argument("--geri-al", metavar="OUTPUTS_DIR", default=None,
                    help="bring each document's newest version back from yedekler/ and exit")
    ap.add_argument("--kuru", action="store_true", help="with --supur / --geri-al: list only, move nothing")
    ap.add_argument("--outputs-dir", help="the workspace's outputs_dir")
    ap.add_argument("--ad", help="base name (old stamp/_vN/extension are stripped)")
    ap.add_argument("--uzanti", help="extension = subfolder (pptx, docx, md, png …)")
    ap.add_argument("--damga", default=None, help="job-start stamp 'YYYYMMDD HHMM' (default: now)")
    ap.add_argument("--ek", default="", help="suffix before the stamp (_zref, _poster, -grid)")
    ap.add_argument("--paket", action="store_true", help="return a package FOLDER, not a file")
    ap.add_argument("--kaynak", action="append", default=[],
                    help="a file this job reads from the target folder: not moved this run (repeatable)")
    a = ap.parse_args(argv)
    for kip, islem in ((a.supur, supur), (a.geri_al, geri_al)):
        if kip:
            if not os.path.isdir(kip):
                print(json.dumps({"error": "no_outputs_dir", "message": kip}, ensure_ascii=False))
                return 2
            print(json.dumps(islem(kip, kuru=a.kuru), ensure_ascii=False, indent=1))
            return 0
    if not (a.outputs_dir and a.ad and a.uzanti):
        ap.error("--outputs-dir, --ad and --uzanti are required (or --supur)")
    stamp = a.damga or damga()
    try:
        u = _uzanti(a.uzanti)
        y = yedekle(os.path.join(os.path.abspath(a.outputs_dir), u), stamp,
                    anahtar_normalle(f"{sade_ad(a.ad)}{a.ek}"), haric=a.kaynak)
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
