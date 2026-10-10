#!/usr/bin/env python3
"""Highlight given phrases in a COPY of a PDF so the user can see where a cited claim appears.

Part of the `journalresearch` skill. Deterministic helper: the skill names the sentence it cited
and the source PDF; this script marks every hit with a highlight annotation in a new file and
reports which page carries it. The source PDF is never modified.

Canonical invocation (the plugin never installs packages into the machine's Python):
    uv run --with pymupdf python journalresearch_pdfvurgula.py <source.pdf> --cikti <dest.pdf> \\
        --ifade "<phrase>" [--ifade "<phrase>" ...] [--etiket "<label>" ...] \\
        [--renk sari|yesil|mavi] [--buyuk-kucuk-duyarsiz] [--uzerine-yaz]

    python journalresearch_pdfvurgula.py paper.pdf --cikti paper_vurgu.pdf \\
        --ifade "30 cc per 24 hours" --ifade "should be tacked down with suture" --etiket "drain" --etiket "suture"

`--etiket` values pair with `--ifade` values by position; a phrase without a label gets the
phrase's first 40 characters as its annotation title. `--not` pairs the same way and becomes the
annotation's text (default: the phrase itself) — e.g. where the passage was cited.
`--sayfa-notu` adds a sticky note on page 1 for a citation that has no passage to mark; a run
with only sticky notes still writes the copy. `--json-girdi FILE` takes the same data as
`{"ifadeler": [{"ifade", "etiket", "not", "sayfa"}], "sayfa_notlari": [...]}` (long or non-ASCII
notes survive no shell quoting); an item's `sayfa` (1-based) is searched first, the whole
document only when the phrase misses there. `--ocr` searches a scanned PDF through Tesseract
(`TESSDATA_PREFIX`, else `C:\\Program Files\\Tesseract-OCR\\tessdata`); the highlight lands on the
page image.

Matching: every page is searched with `page.search_for(phrase, quads=True)`. If the exact phrase
has no hit on any page, the search is retried with whitespace normalised and then with the
phrase's 6-word windows, longest first, the first one that hits winning (reported as
`eslesme: "tam" | "kirpilmis" | "yok"`; a fallback never runs beside a full hit). With
`--buyuk-kucuk-duyarsiz` the page text is searched case-insensitively instead.

Output: JSON to stdout:
    {"kaynak": "...", "cikti": "...", "sayfa_sayisi": N,
     "ifadeler": [{"ifade": "...", "etiket": "...", "eslesme": "tam", "sayfalar": [1, 6], "vuruş": 2}],
     "bulunmayan": ["..."]}

Exit codes: 0 — the output file was written (even if some phrases were not found);
1 — NO phrase was found and no sticky note was asked, nothing is written; 2 — refused before any
work: PyMuPDF missing (`{"error": "no_pymupdf"}`), source unreadable, `--cikti` resolves to the
source (`same_path`), `--cikti` already exists without `--uzerine-yaz` (`exists`), an unreadable
`--json-girdi` (`bad_json`) or nothing to do (`nothing_to_do`).
"""
import argparse
import json
import os
import re
import sys


def _get_pymupdf():
    """Return the PyMuPDF module (`pymupdf`, else the legacy `fitz` name), or None."""
    try:
        import pymupdf  # type: ignore
        return pymupdf
    except Exception:
        pass
    try:
        import fitz  # type: ignore
        return fitz
    except Exception:
        return None


_COLORS = {
    "sari": (1.0, 1.0, 0.0),
    "yesil": (0.6, 1.0, 0.6),
    "mavi": (0.6, 0.8, 1.0),
}


def _normalize_ws(text):
    return re.sub(r"\s+", " ", text).strip()


def _windows(phrase, size=6):
    """Every 6-word window of the phrase, longest (most specific) first; [] for short phrases."""
    words = _normalize_ws(phrase).split(" ")
    if len(words) <= size:
        return []
    windows = [" ".join(words[i:i + size]) for i in range(len(words) - size + 1)]
    return sorted(windows, key=len, reverse=True)


_TESSDATA_DEFAULT = r"C:\Program Files\Tesseract-OCR\tessdata"
_OCR_CACHE = {}


def _textpage(page, ocr):
    """(page, OCR text page) for a scanned page, or (page, None) for the PDF's own text layer.

    The OCR text page is bound to the Page object that made it: `doc[n]` returns a new object
    each call, so the cache keeps that Page alive and hands it back with its text page.
    """
    if not ocr:
        return page, None
    key = (id(page.parent), page.number)
    if key not in _OCR_CACHE:
        tessdata = os.environ.get("TESSDATA_PREFIX") or _TESSDATA_DEFAULT
        _OCR_CACHE[key] = (page, page.get_textpage_ocr(language="eng", dpi=300, full=True, tessdata=tessdata))
    return _OCR_CACHE[key]


def _search_page(page, needle, case_insensitive, ocr=False):
    """List of quads/rects for `needle` on `page`; empty when there is no hit.

    `search_for()` is case-sensitive in every PyMuPDF release; the case-insensitive path
    walks the page's word list instead and returns one rect per matched word. With `ocr`
    both search the page's Tesseract text instead of its (absent) text layer.
    """
    try:
        page, tp = _textpage(page, ocr)
        if case_insensitive:
            return _search_ci(page, needle, tp)
        return page.search_for(needle, quads=True, textpage=tp)
    except Exception:
        return []


_PUNCT = ".,;:()[]{}\"'"


def _search_ci(page, needle, tp=None):
    """Case-insensitive fallback: match the needle's words against the page's word sequence."""
    words = page.get_text("words", textpage=tp)  # (x0, y0, x1, y1, word, block, line, wordno)
    needle_words = [w.strip(_PUNCT).lower() for w in _normalize_ws(needle).split(" ")]
    needle_words = [w for w in needle_words if w]
    n = len(needle_words)
    if not words or n == 0:
        return []
    page_words = [w[4].strip(_PUNCT).lower() for w in words]
    rects = []
    for i in range(len(page_words) - n + 1):
        if page_words[i:i + n] == needle_words:
            rects.extend(tuple(w[:4]) for w in words[i:i + n])
    return rects


def _bbox(q):
    """(x0, y0, x1, y1) of a Quad, Rect or 4-tuple."""
    if hasattr(q, "rect"):
        r = q.rect
        return (r.x0, r.y0, r.x1, r.y1)
    if hasattr(q, "x0"):
        return (q.x0, q.y0, q.x1, q.y1)
    return tuple(q[:4])


def _group_hits(quads):
    """Split the page's quads into occurrences.

    `search_for()` returns one quad per line segment, so a phrase wrapping over two lines
    gives two quads for one hit; the CI path gives one rect per word. Consecutive pieces
    that sit on the same line or on the line directly below belong to the same occurrence;
    a jump back up or further down starts a new one.
    """
    groups = []
    prev = None
    for q in quads:
        x0, y0, x1, y1 = _bbox(q)
        if prev is not None:
            px0, py0, px1, py1 = prev
            line_h = max(py1 - py0, 1.0)
            same_line = abs(y0 - py0) < line_h * 0.5 and x0 >= px0 - 2
            next_line = 0 < (y0 - py0) <= line_h * 1.8
            if same_line or next_line:
                groups[-1].append(q)
                prev = (x0, y0, x1, y1)
                continue
        groups.append([q])
        prev = (x0, y0, x1, y1)
    return groups


def _find(doc, phrase, case_insensitive, ocr=False, page_hint=None):
    """`_find_in` on the hinted page (1-based) first; the whole document when it misses there."""
    if page_hint and 1 <= page_hint <= doc.page_count:
        per_page, kind = _find_in(doc, phrase, case_insensitive, ocr, [page_hint - 1])
        if per_page:
            return per_page, kind
    return _find_in(doc, phrase, case_insensitive, ocr, range(doc.page_count))


def _find_in(doc, phrase, case_insensitive, ocr, page_numbers):
    """Document-level search: exact → whitespace-normalised → longest 6-word window.

    A fallback is tried only when the previous form hit NO page, so a phrase found in full
    on page 1 is never also marked by its 6-word window on page 2.
    Returns ({page_index: quads}, kind).
    """
    norm = _normalize_ws(phrase)
    attempts = [(phrase, "tam")]
    if norm != phrase:
        attempts.append((norm, "tam"))
    # Windows are tried longest first and the first one that hits wins (reported "kirpilmis").
    attempts.extend((w, "kirpilmis") for w in _windows(norm))
    for needle, kind in attempts:
        per_page = {}
        for pno in page_numbers:
            quads = _search_page(doc[pno], needle, case_insensitive, ocr)
            if quads:
                per_page[pno] = quads
        if per_page:
            return per_page, kind
    return {}, "yok"


def highlight(mod, source, dest, phrases, labels, color, case_insensitive,
              notes=(), page_notes=(), ocr=False, page_hints=()):
    doc = mod.open(source)
    try:
        page_count = doc.page_count
        results = []
        # Search everything before the first annotation: an annotation changes the page, and a
        # cached OCR text page is no longer searchable afterwards.
        found = [_find(doc, phrase, case_insensitive, ocr,
                       page_hints[idx] if idx < len(page_hints) else None)
                 for idx, phrase in enumerate(phrases)]
        _OCR_CACHE.clear()
        for idx, phrase in enumerate(phrases):
            label = labels[idx] if idx < len(labels) and labels[idx] else phrase[:40]
            note = notes[idx] if idx < len(notes) and notes[idx] else phrase
            pages = []
            hits = 0
            per_page, kind_overall = found[idx]
            for pno in sorted(per_page):
                page = doc[pno]
                for group in _group_hits(per_page[pno]):
                    annot = page.add_highlight_annot(group)
                    annot.set_colors(stroke=color)
                    annot.set_info(title=label, content=note)
                    annot.update()
                    hits += 1
                pages.append(pno + 1)
            results.append({
                "ifade": phrase,
                "etiket": label,
                "eslesme": kind_overall,
                "sayfalar": pages,
                "vuruş": hits,
            })
        # Sticky notes for what has no passage to mark, stacked down the first page's left margin.
        first = doc[0] if page_count else None
        for n, text in enumerate(page_notes):
            annot = first.add_text_annot((12, 24 + 26 * n), text, icon="Comment")
            annot.set_info(title="Not", content=text)
            annot.update()
        found_any = any(r["vuruş"] for r in results) or bool(page_notes)
        if found_any:
            doc.save(dest, garbage=0, deflate=True)
        return page_count, results, found_any
    finally:
        doc.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Highlight phrases in a copy of a PDF.")
    ap.add_argument("kaynak", help="Source PDF (never modified).")
    ap.add_argument("--cikti", required=True, help="Destination PDF (must differ from the source).")
    ap.add_argument("--ifade", action="append", default=[], metavar="PHRASE",
                    help="Phrase to highlight; repeat for several.")
    ap.add_argument("--etiket", action="append", default=[], metavar="LABEL",
                    help="Annotation title paired with --ifade by position (default: phrase[:40]).")
    ap.add_argument("--not", dest="notlar", action="append", default=[], metavar="NOTE",
                    help="Annotation text paired with --ifade by position (default: the phrase).")
    ap.add_argument("--sayfa-notu", action="append", default=[], metavar="NOTE",
                    help="Sticky note on page 1 for something with no passage to mark; repeatable.")
    ap.add_argument("--ocr", action="store_true",
                    help="Scanned PDF: search Tesseract OCR text (TESSDATA_PREFIX or the default install).")
    ap.add_argument("--json-girdi", metavar="FILE",
                    help="UTF-8 JSON {ifadeler:[{ifade,etiket,not}], sayfa_notlari:[...]} instead of "
                         "repeated flags (long notes, many phrases).")
    ap.add_argument("--renk", choices=sorted(_COLORS), default="sari",
                    help="Highlight colour (default sari).")
    ap.add_argument("--buyuk-kucuk-duyarsiz", action="store_true",
                    help="Case-insensitive matching.")
    ap.add_argument("--uzerine-yaz", action="store_true",
                    help="Allow overwriting an existing --cikti.")
    args = ap.parse_args(argv)

    # Windows consoles default to a legacy codepage (e.g. cp1254) that can't encode
    # many characters found in PDFs; force UTF-8 so JSON output never crashes.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    def out(obj):
        print(json.dumps(obj, ensure_ascii=False, indent=2))

    phrases, labels, notes, page_notes = list(args.ifade), list(args.etiket), list(args.notlar), list(args.sayfa_notu)
    page_hints = []
    if args.json_girdi:
        try:
            spec = json.load(open(args.json_girdi, encoding="utf-8"))
        except Exception as e:
            out({"error": "bad_json", "message": str(e)})
            return 2
        for item in spec.get("ifadeler", []):
            # Pad the flag lists so positions stay paired once JSON items follow flag items.
            labels += [""] * (len(phrases) - len(labels))
            notes += [""] * (len(phrases) - len(notes))
            page_hints += [None] * (len(phrases) - len(page_hints))
            phrases.append(item["ifade"])
            labels.append(item.get("etiket", ""))
            notes.append(item.get("not", ""))
            page_hints.append(item.get("sayfa"))
        page_notes += spec.get("sayfa_notlari", [])
    if not phrases and not page_notes:
        out({"error": "nothing_to_do", "message": "Give --ifade, --sayfa-notu or --json-girdi."})
        return 2

    mod = _get_pymupdf()
    if mod is None:
        out({"error": "no_pymupdf",
             "hint": "uv run --with pymupdf python journalresearch_pdfvurgula.py …"})
        return 2

    source = os.path.abspath(args.kaynak)
    dest = os.path.abspath(args.cikti)
    if not os.path.isfile(source):
        out({"error": "bad_source", "message": f"Not a file: {source}"})
        return 2
    if os.path.normcase(source) == os.path.normcase(dest):
        out({"error": "same_path", "message": "--cikti must not be the source PDF."})
        return 2
    if os.path.exists(dest) and not args.uzerine_yaz:
        out({"error": "exists", "message": f"{dest} already exists; pass --uzerine-yaz to replace it."})
        return 2
    dest_dir = os.path.dirname(dest)
    if dest_dir and not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    try:
        page_count, results, found_any = highlight(
            mod, source, dest, phrases, labels, _COLORS[args.renk], args.buyuk_kucuk_duyarsiz,
            notes, page_notes, args.ocr, page_hints)
    except Exception as e:
        out({"error": "unreadable", "message": str(e), "kaynak": source})
        return 2

    report = {
        "kaynak": source,
        "cikti": dest if found_any else None,
        "sayfa_sayisi": page_count,
        "ifadeler": results,
        "bulunmayan": [r["ifade"] for r in results if r["eslesme"] == "yok"],
    }
    if page_notes:
        report["sayfa_notlari"] = len(page_notes)
    if not found_any:
        report["message"] = "No phrase was found; nothing was written."
        out(report)
        return 1
    out(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
