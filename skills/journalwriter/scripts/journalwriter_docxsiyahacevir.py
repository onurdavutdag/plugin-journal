#!/usr/bin/env python3
"""
"siyaha çevir" — turn a marked docx revision round into a clean copy (#843, 2026-11-07).

The inverse of `journalwriter_docxisaretliduzelt.py`: every struck-through run (w:strike / w:dstrike)
is DELETED, every run coloured with the marking colour (default 0070C0, the user's blue) loses its
colour and prints black. Highlights (the cyan "(eklenecek)" placeholders, the user's green/red/yellow)
are left untouched and counted, so the caller can say what is still marked. A run that carries a
field character or field code is never removed, even when struck: removing half a field breaks Word.

Usage:
    python -B journalwriter_docxsiyahacevir.py <file.docx> [--apply] [--renk 0070C0] [--cikti <out.docx>]
                                               [--kilide-ragmen]

Default is a DRY run: nothing is written, the JSON report says what would change. `--apply` writes
the result over <file.docx> (the user's in-place rule) or to `--cikti`. After an in-place write the
CALLER restamps the file to its last-change stamp (journalwriter SKILL.md, #824) and re-exports the
PDF; this script does not rename anything.

Refuses (exit 3) while Word's owner file `~$…` sits beside the input — the user's unsaved changes
are not in the file being read (#605). `--kilide-ragmen` overrides on purpose.

Report (stdout, one JSON): {"file", "applied", "struck_runs_removed", "struck_text", "colour_runs_blackened",
"left_struck", "left_colour", "highlights_kept", "fields_before", "fields_after", "skipped_field_runs", "output"}.
Exit 0 ok, 1 usage/format error, 2 field count changed (nothing written), 3 Word lock.

Windows note (#842): every zip handle is closed before the replace — an open `ZipFile(src)` makes
`os.replace(tmp, src)` fail with WinError 5.
"""
import argparse
import json
import os
import sys
import zipfile

try:
    from lxml import etree
except ImportError:  # pragma: no cover
    print(json.dumps({"error": "lxml_missing", "hint": "uv run --with lxml python -B <this script> ..."}))
    sys.exit(1)

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
PARTS = ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml")


def _on(el):
    if el is None:
        return False
    return el.get("{%s}val" % W) not in ("0", "false", "off")


def _field_count(root):
    return sum(1 for t in root.iter("{%s}instrText" % W) if "ADDIN ZOTERO_ITEM" in (t.text or ""))


def temizle(root, renk):
    rep = {"struck_runs_removed": 0, "struck_text": [], "colour_runs_blackened": 0, "skipped_field_runs": 0}
    for r in list(root.iter("{%s}r" % W)):
        rpr = r.find("w:rPr", NS)
        if rpr is None:
            continue
        if _on(rpr.find("w:strike", NS)) or _on(rpr.find("w:dstrike", NS)):
            if r.find("w:fldChar", NS) is not None or r.find("w:instrText", NS) is not None:
                rep["skipped_field_runs"] += 1
                continue
            rep["struck_runs_removed"] += 1
            rep["struck_text"].append("".join(t.text or "" for t in r.iter("{%s}t" % W)))
            r.getparent().remove(r)
            continue
        c = rpr.find("w:color", NS)
        if c is not None and (c.get("{%s}val" % W) or "").upper() == renk:
            rpr.remove(c)
            rep["colour_runs_blackened"] += 1
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description="Clean a marked docx: delete struck runs, marking colour to black.")
    ap.add_argument("girdi")
    ap.add_argument("--apply", action="store_true", help="write (default: dry run)")
    ap.add_argument("--renk", default="0070C0", help="marking colour RRGGBB (default 0070C0)")
    ap.add_argument("--cikti", help="write here instead of over the input")
    ap.add_argument("--kilide-ragmen", action="store_true", help="write even while Word's ~$ lock exists")
    a = ap.parse_args(argv)
    src = os.path.abspath(a.girdi)
    renk = a.renk.upper().lstrip("#")
    if not os.path.isfile(src) or not src.lower().endswith(".docx"):
        print(json.dumps({"error": "not_a_docx", "file": src}, ensure_ascii=False))
        return 1
    d, ad = os.path.split(src)
    # Word's owner file drops the first two characters of a long name ("~$cdef.docx" for "abcdef.docx")
    locked = any(n.startswith("~$") and n[2:] in (ad, ad[2:]) for n in os.listdir(d))
    if a.apply and not a.kilide_ragmen and locked:
        print(json.dumps({"error": "word_lock", "file": src, "hint": "close the document in Word, then rerun"},
                         ensure_ascii=False))
        return 3
    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        raw = {p: z.read(p) for p in PARTS if p in names}
    rep = {"file": src, "applied": False, "struck_runs_removed": 0, "struck_text": [], "colour_runs_blackened": 0,
           "skipped_field_runs": 0, "left_struck": 0, "left_colour": 0, "highlights_kept": {},
           "fields_before": 0, "fields_after": 0, "output": None}
    roots = {}
    for p, data in raw.items():
        root = etree.fromstring(data)
        rep["fields_before"] += _field_count(root)
        r = temizle(root, renk)
        for k in ("struck_runs_removed", "colour_runs_blackened", "skipped_field_runs"):
            rep[k] += r[k]
        rep["struck_text"] += r["struck_text"]
        rep["fields_after"] += _field_count(root)
        rep["left_struck"] += sum(1 for e in root.iter("{%s}strike" % W) if _on(e))
        rep["left_colour"] += len(root.xpath('//w:color[translate(@w:val,"abcdef","ABCDEF")="%s"]' % renk,
                                             namespaces=NS))
        for h in root.iter("{%s}highlight" % W):
            v = h.get("{%s}val" % W)
            rep["highlights_kept"][v] = rep["highlights_kept"].get(v, 0) + 1
        roots[p] = root
    if rep["fields_after"] != rep["fields_before"]:
        rep["error"] = "field_count_changed"
        print(json.dumps(rep, ensure_ascii=False))
        return 2
    if a.apply:
        out = os.path.abspath(a.cikti) if a.cikti else src
        tmp = out + ".siyah.tmp"
        with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            for it in zin.infolist():
                data = zin.read(it.filename)
                if it.filename in roots:
                    data = etree.tostring(roots[it.filename], xml_declaration=True, encoding="UTF-8", standalone=True)
                zo.writestr(it, data)
        os.replace(tmp, out)
        rep["applied"] = True
        rep["output"] = out
    print(json.dumps(rep, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
