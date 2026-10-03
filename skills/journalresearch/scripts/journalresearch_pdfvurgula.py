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
phrase's first 40 characters as its annotation title.

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
1 — NO phrase was found, nothing is written; 2 — refused before any work: PyMuPDF missing
(`{"error": "no_pymupdf"}`), source unreadable, `--cikti` resolves to the source (`same_path`),
or `--cikti` already exists without `--uzerine-yaz` (`exists`).
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


def _search_page(page, needle, case_insensitive):
    """List of quads/rects for `needle` on `page`; empty when there is no hit.

    `search_for()` is case-sensitive in every PyMuPDF release; the case-insensitive path
    walks the page's word list instead and returns one rect per matched word.
    """
    try:
        if case_insensitive:
            return _search_ci(page, needle)
        return page.search_for(needle, quads=True)
    except Exception:
        return []


_PUNCT = ".,;:()[]{}\"'"


def _search_ci(page, needle):
    """Case-insensitive fallback: match the needle's words against the page's word sequence."""
    words = page.get_text("words")  # (x0, y0, x1, y1, word, block, line, wordno)
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


def _find(doc, phrase, case_insensitive):
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
        for pno in range(doc.page_count):
            quads = _search_page(doc[pno], needle, case_insensitive)
            if quads:
                per_page[pno] = quads
        if per_page:
            return per_page, kind
    return {}, "yok"


def highlight(mod, source, dest, phrases, labels, color, case_insensitive):
    doc = mod.open(source)
    try:
        page_count = doc.page_count
        results = []
        for idx, phrase in enumerate(phrases):
            label = labels[idx] if idx < len(labels) and labels[idx] else phrase[:40]
            pages = []
            hits = 0
            per_page, kind_overall = _find(doc, phrase, case_insensitive)
            for pno in sorted(per_page):
                page = doc[pno]
                for group in _group_hits(per_page[pno]):
                    annot = page.add_highlight_annot(group)
                    annot.set_colors(stroke=color)
                    annot.set_info(title=label, content=phrase)
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
        found_any = any(r["vuruş"] for r in results)
        if found_any:
            doc.save(dest, garbage=0, deflate=True)
        return page_count, results, found_any
    finally:
        doc.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Highlight phrases in a copy of a PDF.")
    ap.add_argument("kaynak", help="Source PDF (never modified).")
    ap.add_argument("--cikti", required=True, help="Destination PDF (must differ from the source).")
    ap.add_argument("--ifade", action="append", required=True, metavar="PHRASE",
                    help="Phrase to highlight; repeat for several.")
    ap.add_argument("--etiket", action="append", default=[], metavar="LABEL",
                    help="Annotation title paired with --ifade by position (default: phrase[:40]).")
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
            mod, source, dest, args.ifade, args.etiket, _COLORS[args.renk], args.buyuk_kucuk_duyarsiz)
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
    if not found_any:
        report["message"] = "No phrase was found; nothing was written."
        out(report)
        return 1
    out(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
