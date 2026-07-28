#!/usr/bin/env python3
"""Search every PDF in a directory for keyword/phrase hits.

Part of the `journalresearch` skill. Deterministic helper so each invocation of the skill
doesn't re-implement PDF text extraction.

Usage:
    python journalresearch_pdfara.py --dir <workspace-or-project-dir> --terms "phrase one" "keyword" ...
    python journalresearch_pdfara.py --dir . --terms "postoperative delirium" dexmedetomidine --context 240

Output: JSON to stdout — a list of hits:
    [{"file": "...", "page": 5, "section_heading": "Results", "snippet": "..."}]

Extraction backend: tries pypdf, then PyPDF2, then pdfplumber. If none is installed,
prints a JSON object with an "error" telling the caller to read the PDFs directly with
the Read tool (which renders PDF pages). Exit code stays 0 so the caller can parse it.
"""
import argparse
import json
import os
import re
import sys


def _get_extractor():
    """Return (name, page_text_fn) for the first available PDF backend, or (None, None).

    page_text_fn(path) -> list[str], one string per page.
    """
    try:
        from pypdf import PdfReader  # type: ignore

        def extract(path):
            reader = PdfReader(path)
            return [(p.extract_text() or "") for p in reader.pages]

        return "pypdf", extract
    except Exception:
        pass

    try:
        from PyPDF2 import PdfReader  # type: ignore

        def extract(path):
            reader = PdfReader(path)
            return [(p.extract_text() or "") for p in reader.pages]

        return "PyPDF2", extract
    except Exception:
        pass

    try:
        import pdfplumber  # type: ignore

        def extract(path):
            with pdfplumber.open(path) as pdf:
                return [(pg.extract_text() or "") for pg in pdf.pages]

        return "pdfplumber", extract
    except Exception:
        pass

    return None, None


# Common biomedical section headings, matched case-insensitively at a line start.
_HEADING_RE = re.compile(
    r"^\s*(abstract|introduction|background|methods?|materials and methods|"
    r"results?|discussion|conclusions?|limitations?|references|"
    r"table\s+\d+|figure\s+\d+|fig\.\s*\d+)\b",
    re.IGNORECASE,
)


def _nearest_heading(page_text, match_pos):
    """Best-effort nearest section heading at or above match_pos in the page text."""
    heading = None
    for m in _HEADING_RE.finditer(page_text):
        if m.start() <= match_pos:
            heading = m.group(1).strip().title()
        else:
            break
    return heading


def _find_pdfs(root):
    pdfs = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, f))
    return sorted(pdfs)


def search(directory, terms, context):
    name, extract = _get_extractor()
    if extract is None:
        return {
            "error": "no_pdf_extractor",
            "message": (
                "No PDF text extractor is installed (tried pypdf, PyPDF2, pdfplumber). "
                "Install one with `pip install pypdf`, or read the candidate PDFs "
                "directly with the Read tool, which renders PDF pages."
            ),
        }

    lowered = [t.lower() for t in terms]
    hits = []
    for path in _find_pdfs(directory):
        try:
            pages = extract(path)
        except Exception as e:  # unreadable/encrypted PDF — note and continue
            hits.append({"file": path, "page": None, "section_heading": None,
                         "snippet": f"[could not read: {e}]"})
            continue
        for i, text in enumerate(pages, start=1):
            if not text:
                continue
            low = text.lower()
            for term in lowered:
                pos = low.find(term)
                if pos == -1:
                    continue
                start = max(0, pos - context // 2)
                end = min(len(text), pos + len(term) + context // 2)
                snippet = re.sub(r"\s+", " ", text[start:end]).strip()
                hits.append({
                    "file": path,
                    "page": i,
                    "section_heading": _nearest_heading(text, pos),
                    "snippet": snippet,
                    "matched_term": term,
                })
                break  # one hit per page is enough to flag it for confirmation
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description="Search PDFs for keyword/phrase hits.")
    ap.add_argument("--dir", required=True, help="Directory to search recursively for PDFs.")
    ap.add_argument("--terms", required=True, nargs="+",
                    help="One or more keywords/phrases (case-insensitive).")
    ap.add_argument("--context", type=int, default=240,
                    help="Chars of surrounding context per snippet (default 240).")
    args = ap.parse_args(argv)

    # Windows consoles default to a legacy codepage (e.g. cp1254) that can't encode
    # many characters found in PDFs; force UTF-8 so JSON output never crashes.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if not os.path.isdir(args.dir):
        print(json.dumps({"error": "bad_dir", "message": f"Not a directory: {args.dir}"}))
        return 0

    result = search(args.dir, args.terms, args.context)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
