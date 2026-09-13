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
  and audits in one package because its asset check refuses paths outside the manifest dir).

Usage (CLI, one JSON on stdout, exit 0 / 2):
    python cikti_yolcoz.py --outputs-dir DIR --ad NAME --uzanti EXT [--damga "YYYYMMDD HHMM"]
                           [--ek SUFFIX] [--paket]
    → {"path", "klasor", "ad", "damga", "paket"}

Library:
    from cikti_yolcoz import damga, sade_ad, yol
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


def _uzanti(uzanti):
    u = uzanti.strip().lstrip(".").lower()
    if not u or not u.isalnum():
        raise ValueError(f"bad extension: {uzanti!r}")
    return u


def yol(outputs_dir, ad, uzanti, damga_str, ek="", paket=False):
    """Absolute destination path; the extension folder is created, the file is not.

    `ek` is a suffix glued to the bare name before the stamp (`_zref`, `_poster`, `-grid`).
    `paket=True` returns (and creates) a folder `<ext>/<name><ek> <stamp>` instead of a file.
    """
    if not STAMP_RE.match(damga_str or ""):
        raise ValueError(f"bad stamp: {damga_str!r} (expected 'YYYYMMDD HHMM')")
    u = _uzanti(uzanti)
    klasor = os.path.join(os.path.abspath(outputs_dir), u)
    os.makedirs(klasor, exist_ok=True)
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
    ap.add_argument("--outputs-dir", required=True, help="the workspace's outputs_dir")
    ap.add_argument("--ad", required=True, help="base name (old stamp/_vN/extension are stripped)")
    ap.add_argument("--uzanti", required=True, help="extension = subfolder (pptx, docx, md, png …)")
    ap.add_argument("--damga", default=None, help="job-start stamp 'YYYYMMDD HHMM' (default: now)")
    ap.add_argument("--ek", default="", help="suffix before the stamp (_zref, _poster, -grid)")
    ap.add_argument("--paket", action="store_true", help="return a package FOLDER, not a file")
    a = ap.parse_args(argv)
    stamp = a.damga or damga()
    try:
        p = yol(a.outputs_dir, a.ad, a.uzanti, stamp, ek=a.ek, paket=a.paket)
    except ValueError as exc:
        code = "bad_stamp" if "stamp" in str(exc) else "bad_extension"
        print(json.dumps({"error": code, "message": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"path": p, "klasor": os.path.dirname(p), "ad": os.path.basename(p),
                      "damga": stamp, "paket": a.paket}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
