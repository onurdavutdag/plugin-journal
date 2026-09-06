#!/usr/bin/env python3
"""Inventory and read the raw material in `<home>/input/` (docx · pdf · pptx · xlsx · csv · md · txt).

Owned by no skill (plugin-root script); read by journalwriter, journalstyle,
journalpeerreview and journalresearch. Imports no skill module. The home is resolved
by `hammadde_kokcoz.py` (same folder); `--home DIR` overrides it (tests, ad-hoc runs).

This script extracts CONTENT (text, outline, sheet rows). It does NOT compute the
structural docx metrics (word count, margins, table/figure count) — those belong to
`skills/journalstyle/scripts/journalstyle_docxyapicikar.py`, one authority per job.

Usage:
    python hammadde_oku.py --list [--home DIR]
    python hammadde_oku.py <file> [--full] [--max-chars N] [--outline] [--heading "Tartışma"]
                                  [--sheet NAME] [--max-rows N] [--pages 3-7] [--home DIR]

`<file>` is absolute, or relative to `<home>/input/`.

`--list` inventories `input/` — excluding the `yayinstili/` and `authorguidelines/`
subtrees (journal material, not manuscript raw material) and `~$*` Office lock files.

Read mode prints one JSON object:
    {"file", "type", "backend", "ok", "summary", "text", "total_chars", "truncated", "warnings"}
Default preview 1500 chars; `--full` 20000; `--max-chars` overrides (same defaults as
`journalstyle_pdfmetincikar.py`). `--outline` returns only headings / slide titles /
sheet names. `--heading X` returns the text from that docx heading to the next heading of
the same or higher level (pptx: the slide whose title matches).

Backends and graceful degradation (no pip package is required for any format):
    docx  python-docx                 → zip + word/document.xml (w:t)
    pdf   fitz → pypdf → PyPDF2 → pdfplumber → {"error": "no_pdf_extractor"} (use the Read tool)
    pptx  python-pptx                 → zip + ppt/slides/slideN.xml (a:t) + notesSlides
    xlsx  openpyxl (data_only)        → zip + sharedStrings + worksheets (formulas lost)
    csv   stdlib csv + Sniffer; encoding ladder utf-8-sig → utf-8 → cp1254 → latin-1
    md/txt same encoding ladder
A corrupt file yields {"ok": false, "error": "unreadable"}; exit code stays 0 so the
caller can parse it. Only a missing home (`no_input_root`) exits 2 (from hammadde_kokcoz).
"""
import argparse
import csv
import datetime
import io
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hammadde_kokcoz import resolve_home, InputRootNotFound  # noqa: E402

TYPES = ["docx", "pdf", "pptx", "xlsx", "csv", "md", "txt"]
JOURNAL_DIRS = ("yayinstili", "authorguidelines")
ENCODINGS = ("utf-8-sig", "utf-8", "cp1254", "latin-1")
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}


# ----------------------------------------------------------------------------- helpers
def _has(module):
    try:
        __import__(module)
        return True
    except Exception:
        return False


def backends():
    pdf = next((m for m in ("fitz", "pypdf", "PyPDF2", "pdfplumber") if _has(m)), None)
    return {
        "docx": "python-docx" if _has("docx") else "zipxml",
        "pdf": pdf,
        "pptx": "python-pptx" if _has("pptx") else "zipxml",
        "xlsx": "openpyxl" if _has("openpyxl") else "zipxml",
        "csv": "csv",
        "md": "builtin",
        "txt": "builtin",
    }


def _read_text_file(path):
    last = None
    for enc in ENCODINGS:
        try:
            with open(path, encoding=enc) as f:
                return f.read(), enc
        except UnicodeDecodeError as e:
            last = e
    raise last


def _numkey(name):
    m = re.search(r"(\d+)\.xml$", name)
    return int(m.group(1)) if m else 0


def _col_index(ref):
    """'BC12' -> 55 (1-based column index)."""
    letters = re.match(r"[A-Z]+", ref)
    n = 0
    for ch in (letters.group(0) if letters else "A"):
        n = n * 26 + (ord(ch) - 64)
    return n


# ----------------------------------------------------------------------------- docx
def _inferred_level(p, text):
    """Heading level for a paragraph WITHOUT a heading style, or None.

    Theses often carry one custom body style for everything ("C2 TEZ") and mark headings
    only visually. Two signals, in order: an explicit outline level (w:outlineLvl) → that
    level + 1; otherwise a short (≤ 90 chars), sentence-free line whose every run is bold →
    level 9 ("inferred", unknown depth). Body text never trips this: it is long, or not
    bold throughout, or ends with a period.
    """
    pPr = p._p.pPr
    if pPr is not None:
        ol = pPr.find("{%s}outlineLvl" % NS["w"])
        if ol is not None:
            try:
                return int(ol.get("{%s}val" % NS["w"])) + 1
            except (TypeError, ValueError):
                pass
    if len(text) > 90 or text.endswith((".", ",", ";", ":")) or not p.runs:
        return None
    runs = [r for r in p.runs if r.text.strip()]
    bold = runs and all(r.bold or (r.style is not None and "bold" in r.style.name.lower())
                        for r in runs)
    caps = text.isupper() and any(ch.isalpha() for ch in text) and len(text.split()) <= 8
    if not (bold or caps):
        return None
    # "5. TARTIŞMA" → 1, "5.1. Sınırlılıklar" → 2, "5.1.2 …" → 3; unnumbered → 9 (unknown)
    m = re.match(r"^(\d+(?:\.\d+)*)\.?\s", text)
    return m.group(1).count(".") + 1 if m else 9


def read_docx(path, warnings):
    """Return (backend, blocks) — blocks: [{"kind": "p"|"h"|"table", "level", "text"}]."""
    try:
        import docx  # python-docx
        d = docx.Document(path)
        blocks = []
        for p in d.paragraphs:
            t = p.text.strip()
            if not t:
                continue
            style = (p.style.name if p.style is not None else "") or ""
            m = re.match(r"(?i)heading\s*(\d+)|başlık\s*(\d+)", style)
            if m or style.lower() == "title":
                lvl = int(m.group(1) or m.group(2)) if m else 0
                blocks.append({"kind": "h", "level": lvl, "text": t})
                continue
            lvl = _inferred_level(p, t)
            if lvl is not None:
                blocks.append({"kind": "h", "level": lvl, "text": t, "inferred": True})
            else:
                blocks.append({"kind": "p", "level": None, "text": t})
        for ti, table in enumerate(d.tables, 1):
            rows = []
            for row in table.rows:
                cells = []
                for c in row.cells:
                    ct = c.text.strip().replace("\n", " ")
                    if not cells or cells[-1] != ct:  # merged cells repeat
                        cells.append(ct)
                rows.append(" | ".join(cells))
            blocks.append({"kind": "table", "level": ti, "text": "\n".join(rows)})
        return "python-docx", blocks
    except ImportError:
        warnings.append("python-docx not installed — zip/XML fallback: headings inferred "
                        "from style ids, tables flattened; pip install python-docx")
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    blocks = []
    for p in root.iter("{%s}p" % NS["w"]):
        t = "".join(x.text or "" for x in p.iter("{%s}t" % NS["w"])).strip()
        if not t:
            continue
        ps = p.find("w:pPr/w:pStyle", NS)
        sid = ps.get("{%s}val" % NS["w"]) if ps is not None else ""
        m = re.match(r"(?i)(?:heading|baslk|başlık)(\d+)", sid or "")
        if m:
            blocks.append({"kind": "h", "level": int(m.group(1)), "text": t})
        else:
            blocks.append({"kind": "p", "level": None, "text": t})
    return "zipxml", blocks


def docx_result(path, a, warnings):
    backend, blocks = read_docx(path, warnings)
    headings = [{"level": b["level"], "text": b["text"], "inferred": b.get("inferred", False)}
                for b in blocks if b["kind"] == "h"]
    inferred = sum(1 for h in headings if h["inferred"])
    summary = {
        "paragraphs": sum(1 for b in blocks if b["kind"] == "p"),
        "tables": sum(1 for b in blocks if b["kind"] == "table"),
        "headings": headings if a.outline else len(headings),
        "headings_inferred": inferred,
    }
    if inferred:
        warnings.append(f"{inferred} heading(s) inferred from bold/uppercase lines (no heading "
                        "style in the document) — level 9 = unknown depth; --heading matches them too")
    if a.outline:
        return backend, summary, ""
    if a.heading:
        want = a.heading.strip().lower()
        start = next((i for i, b in enumerate(blocks)
                      if b["kind"] == "h" and want in b["text"].lower()), None)
        if start is None:
            warnings.append(f"heading not found: {a.heading!r} — use --outline to list headings")
            return backend, summary, ""
        lvl = blocks[start]["level"] or 0
        out = [blocks[start]["text"]]
        for b in blocks[start + 1:]:
            if b["kind"] == "h" and (b["level"] or 0) <= lvl:
                break
            out.append(b["text"])
        return backend, summary, "\n".join(out)
    return backend, summary, "\n".join(b["text"] for b in blocks)


# ----------------------------------------------------------------------------- pdf
def read_pdf(path, a, warnings):
    pages = None
    backend = None
    if _has("fitz"):
        import fitz
        doc = fitz.open(path)
        pages = [pg.get_text() for pg in doc]
        backend = "fitz"
    elif _has("pypdf") or _has("PyPDF2"):
        try:
            from pypdf import PdfReader
            backend = "pypdf"
        except ImportError:
            from PyPDF2 import PdfReader
            backend = "PyPDF2"
        pages = [(p.extract_text() or "") for p in PdfReader(path).pages]
    elif _has("pdfplumber"):
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = [(pg.extract_text() or "") for pg in pdf.pages]
        backend = "pdfplumber"
    if pages is None:
        return None, None, None
    total = len(pages)
    if a.pages:
        lo, _, hi = a.pages.partition("-")
        lo = max(1, int(lo))
        hi = min(total, int(hi or lo))
        pages = pages[lo - 1:hi]
    summary = {"pages": total, "selected": a.pages or "all"}
    if a.outline:
        return backend, summary, ""
    return backend, summary, "\n".join(pages)


# ----------------------------------------------------------------------------- pptx
def read_pptx(path, warnings):
    """Return (backend, slides) — slides: [{"n", "title", "text", "notes"}]."""
    try:
        from pptx import Presentation
        prs = Presentation(path)
        slides = []
        for n, s in enumerate(prs.slides, 1):
            title = s.shapes.title.text.strip() if s.shapes.title is not None else ""
            texts = []
            for sh in s.shapes:
                if sh.has_text_frame:
                    t = sh.text_frame.text.strip()
                    if t and t != title:
                        texts.append(t)
                if getattr(sh, "has_table", False) and sh.has_table:
                    for row in sh.table.rows:
                        texts.append(" | ".join(c.text.strip() for c in row.cells))
            notes = ""
            if s.has_notes_slide:
                notes = s.notes_slide.notes_text_frame.text.strip()
            slides.append({"n": n, "title": title, "text": "\n".join(texts), "notes": notes})
        return "python-pptx", slides
    except ImportError:
        warnings.append("python-pptx not installed — zip/XML fallback: text and notes kept, "
                        "shape order approximate, first text box taken as title; "
                        "pip install python-pptx")
    slides = []
    with zipfile.ZipFile(path) as z:
        names = sorted((n for n in z.namelist()
                        if re.match(r"ppt/slides/slide\d+\.xml$", n)), key=_numkey)
        for n_idx, name in enumerate(names, 1):
            root = ET.fromstring(z.read(name))
            paras = []
            for p in root.iter("{%s}p" % NS["a"]):
                t = "".join(x.text or "" for x in p.iter("{%s}t" % NS["a"])).strip()
                if t:
                    paras.append(t)
            title = paras[0] if paras else ""
            notes = ""
            nname = "ppt/notesSlides/notesSlide%d.xml" % _numkey(name)
            if nname in z.namelist():
                nroot = ET.fromstring(z.read(nname))
                notes = "\n".join(
                    "".join(x.text or "" for x in p.iter("{%s}t" % NS["a"])).strip()
                    for p in nroot.iter("{%s}p" % NS["a"])).strip()
                notes = re.sub(r"\n\d+\s*$", "", notes)  # trailing slide-number placeholder
            slides.append({"n": n_idx, "title": title,
                           "text": "\n".join(paras[1:]), "notes": notes})
    return "zipxml", slides


def pptx_result(path, a, warnings):
    backend, slides = read_pptx(path, warnings)
    summary = {"slides": len(slides), "titles": [s["title"] for s in slides]}
    if a.outline:
        return backend, summary, ""
    if a.heading:
        want = a.heading.strip().lower()
        slides = [s for s in slides if want in s["title"].lower()]
        if not slides:
            warnings.append(f"no slide title matches {a.heading!r}")
    parts = []
    for s in slides:
        block = f"--- slide {s['n']}: {s['title']}\n{s['text']}"
        if s["notes"]:
            block += f"\n[notes] {s['notes']}"
        parts.append(block)
    return backend, summary, "\n".join(parts)


# ----------------------------------------------------------------------------- xlsx
def read_xlsx(path, warnings):
    """Return (backend, sheets) — sheets: [{"name", "rows": [[cell,...],...]}]."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        sheets = []
        for ws in wb.worksheets:
            rows = [["" if v is None else v for v in r] for r in ws.iter_rows(values_only=True)]
            sheets.append({"name": ws.title, "rows": rows})
        return "openpyxl", sheets
    except ImportError:
        warnings.append("openpyxl not installed — zip/XML fallback: cached values only "
                        "(formulas without a cached result read empty), dates appear as "
                        "serial numbers; pip install openpyxl")
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            sroot = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sroot.findall("s:si", NS):
                shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["s"])))
        names = {}
        if "xl/workbook.xml" in z.namelist():
            wroot = ET.fromstring(z.read("xl/workbook.xml"))
            for i, sh in enumerate(wroot.findall("s:sheets/s:sheet", NS), 1):
                names[i] = sh.get("name", f"Sheet{i}")
        sheets = []
        sheet_files = sorted((n for n in z.namelist()
                              if re.match(r"xl/worksheets/sheet\d+\.xml$", n)), key=_numkey)
        for name in sheet_files:
            idx = _numkey(name)
            root = ET.fromstring(z.read(name))
            rows = []
            for row in root.iter("{%s}row" % NS["s"]):
                cells = []
                for c in row.findall("s:c", NS):
                    ci = _col_index(c.get("r", "A1"))
                    while len(cells) < ci - 1:
                        cells.append("")
                    v = c.find("s:v", NS)
                    t = c.get("t")
                    if t == "s" and v is not None:
                        val = shared[int(v.text)] if v.text and int(v.text) < len(shared) else ""
                    elif t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["s"]))
                    elif v is not None and v.text is not None:
                        val = v.text
                        try:
                            f = float(val)
                            val = int(f) if f.is_integer() else f
                        except ValueError:
                            pass
                    else:
                        val = ""
                    cells.append(val)
                rows.append(cells)
            sheets.append({"name": names.get(idx, f"Sheet{idx}"), "rows": rows})
    return "zipxml", sheets


def _rows_to_text(rows, max_rows, warnings):
    if max_rows and len(rows) > max_rows:
        warnings.append(f"{len(rows)} rows, first {max_rows} shown — raise --max-rows")
        rows = rows[:max_rows]
    return "\n".join(" | ".join("" if v is None else str(v) for v in r) for r in rows)


def xlsx_result(path, a, warnings):
    backend, sheets = read_xlsx(path, warnings)
    summary = {"sheets": [{"name": s["name"], "rows": len(s["rows"]),
                           "cols": max((len(r) for r in s["rows"]), default=0)} for s in sheets]}
    if a.outline:
        return backend, summary, ""
    if a.sheet:
        sel = [s for s in sheets if s["name"].lower() == a.sheet.lower()]
        if not sel:
            warnings.append(f"sheet not found: {a.sheet!r}; available: "
                            + ", ".join(s["name"] for s in sheets))
        sheets = sel
    parts = [f"--- sheet {s['name']}\n{_rows_to_text(s['rows'], a.max_rows, warnings)}"
             for s in sheets]
    return backend, summary, "\n".join(parts)


# ----------------------------------------------------------------------------- csv / md / txt
def csv_result(path, a, warnings):
    raw, enc = _read_text_file(path)
    sample = raw[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        delim = dialect.delimiter
    except csv.Error:
        delim = ","
    rows = list(csv.reader(io.StringIO(raw), delimiter=delim))
    summary = {"rows": len(rows), "cols": max((len(r) for r in rows), default=0),
               "delimiter": delim, "encoding": enc}
    if a.outline:
        return "csv", summary, ""
    return "csv", summary, _rows_to_text(rows, a.max_rows, warnings)


def text_result(path, a, warnings):
    raw, enc = _read_text_file(path)
    summary = {"lines": raw.count("\n") + 1, "encoding": enc}
    if a.outline:
        heads = [l.strip() for l in raw.splitlines() if l.startswith("#")]
        summary["headings"] = heads
        return "builtin", summary, ""
    return "builtin", summary, raw


# ----------------------------------------------------------------------------- inventory
def inventory(home):
    input_dir = os.path.join(home, "input")
    by_type = {t: [] for t in TYPES}
    unsupported = []
    count = 0
    for dirpath, dirnames, files in os.walk(input_dir):
        if dirpath == input_dir:
            dirnames[:] = [d for d in dirnames if d not in JOURNAL_DIRS]
        for f in sorted(files):
            if f.startswith("~$"):
                continue
            full = os.path.join(dirpath, f)
            ext = os.path.splitext(f)[1].lower().lstrip(".")
            st = os.stat(full)
            entry = {"name": f, "relpath": os.path.relpath(full, input_dir).replace(os.sep, "/"),
                     "size_bytes": st.st_size,
                     "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%dT%H:%M")}
            if ext in by_type:
                by_type[ext].append(entry)
                count += 1
            else:
                unsupported.append({"name": f, "ext": "." + ext if ext else ""})
    journal_dirs = {}
    for d in JOURNAL_DIRS:
        p = os.path.join(input_dir, d)
        journal_dirs[d] = sorted(x for x in os.listdir(p)
                                 if os.path.isdir(os.path.join(p, x))) if os.path.isdir(p) else []
    return {"home": home, "input_dir": input_dir, "count": count, "by_type": by_type,
            "unsupported": unsupported, "journal_dirs": journal_dirs, "backends": backends()}


# ----------------------------------------------------------------------------- main
READERS = {"docx": docx_result, "pdf": read_pdf, "pptx": pptx_result, "xlsx": xlsx_result,
           "csv": csv_result, "md": text_result, "txt": text_result}


def main():
    ap = argparse.ArgumentParser(description="plugin-journal raw-material lister/reader")
    ap.add_argument("file", nargs="?", help="File to read (absolute, or relative to <home>/input/)")
    ap.add_argument("--list", action="store_true", help="Inventory of <home>/input/")
    ap.add_argument("--home", default=None, help="Override the resolved home")
    ap.add_argument("--full", action="store_true", help="Up to 20000 chars instead of 1500")
    ap.add_argument("--max-chars", type=int, default=None)
    ap.add_argument("--outline", action="store_true",
                    help="Headings / slide titles / sheet names only, no body text")
    ap.add_argument("--heading", default=None,
                    help="docx: text under this heading; pptx: the slide with this title")
    ap.add_argument("--sheet", default=None, help="xlsx: only this sheet")
    ap.add_argument("--max-rows", type=int, default=200, help="xlsx/csv row cap (default 200)")
    ap.add_argument("--pages", default=None, help="pdf: page range, e.g. 3-7")
    a = ap.parse_args()

    if a.home:
        home = os.path.abspath(a.home)
        if not os.path.isdir(os.path.join(home, "input")):
            print(json.dumps({"error": "no_input_root",
                              "message": f"--home {home} has no input/ folder"}, ensure_ascii=False))
            return 2
    else:
        try:
            home = resolve_home(scaffold=False)["home"]
        except InputRootNotFound as e:
            print(json.dumps(e.as_json(), ensure_ascii=False, indent=2))
            return 2

    if a.list or not a.file:
        print(json.dumps(inventory(home), ensure_ascii=False, indent=2))
        return 0

    path = a.file
    if not os.path.isabs(path) and not os.path.exists(path):
        cand = os.path.join(home, "input", path)
        if os.path.exists(cand):
            path = cand
    path = os.path.abspath(path)
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    result = {"file": path, "type": ext, "backend": None, "ok": False,
              "summary": {}, "text": "", "total_chars": 0, "truncated": False, "warnings": []}
    if not os.path.isfile(path):
        result.update(error="not_found")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if ext not in READERS:
        result.update(error="unsupported_type",
                      warnings=[f"supported: {', '.join(TYPES)}"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    max_chars = a.max_chars if a.max_chars is not None else (20000 if a.full else 1500)
    warnings = result["warnings"]
    try:
        backend, summary, text = READERS[ext](path, a, warnings)
    except Exception as e:  # corrupt / not really that format
        result.update(error="unreadable", warnings=warnings + [f"{type(e).__name__}: {e}"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if backend is None and ext == "pdf":
        result.update(error="no_pdf_extractor",
                      warnings=warnings + ["No PDF text extractor is installed (tried fitz, pypdf, "
                                           "PyPDF2, pdfplumber). Install one with `pip install pypdf`, "
                                           "or read the PDF directly with the Read tool (pages)."])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    text = text or ""
    result.update(backend=backend, ok=True, summary=summary, total_chars=len(text),
                  truncated=len(text) > max_chars, text=text[:max_chars])
    if result["truncated"]:
        warnings.append(f"text truncated to {max_chars} of {len(text)} chars — use --full, "
                        "--max-chars N, --heading, --sheet or --pages to narrow")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
