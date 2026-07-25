#!/usr/bin/env python3
"""Shared .docx helpers for the journalstyle scripts.

`Document.paragraphs` only covers top-level body paragraphs: table cells, headers,
footers and footnotes are invisible to it, so anything that walks a document for
formatting or counting must go through `iter_paragraphs()` here instead.

Imported by `apply_profile.py` and `extract_docx_structure.py` (same directory).
`zotero_cite.py` keeps its own copy on purpose — a zotero script must not depend on
a journalstyle script (skill boundary, CLAUDE.md §2).
"""
import sys

from docx.oxml.ns import qn

_HEADER_PARTS = ("header", "first_page_header", "even_page_header",
                 "footer", "first_page_footer", "even_page_footer")


def utf8_stdout():
    """Keep Turkish characters alive when stdout is redirected on Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001 — older Python / non-reconfigurable stream
            pass


def _iter_container(container):
    """Paragraphs of a body/cell/header/footer, recursing into (nested) tables."""
    for p in getattr(container, "paragraphs", ()):
        yield p
    for table in getattr(container, "tables", ()):
        for row in table.rows:
            for cell in row.cells:
                yield from _iter_container(cell)


def iter_paragraphs(doc, include_headers=True):
    """Every paragraph of the document: body, tables, headers and footers."""
    yield from _iter_container(doc)
    if not include_headers:
        return
    for section in doc.sections:
        for name in _HEADER_PARTS:
            part = getattr(section, name, None)
            if part is not None:
                yield from _iter_container(part)


def iter_runs(paragraph):
    """Every run of the paragraph — INCLUDING the ones inside a `<w:hyperlink>`.

    `Paragraph.runs` returns direct children only, so a DOI/URL hyperlink in the
    reference list keeps its original font when a profile is applied. Walking
    `.//w:r` catches those too. (`zotero_cite.py` solves the same problem with its
    own copy — the skill boundary forbids importing across skills.)
    """
    from docx.text.run import Run
    return [Run(el, paragraph) for el in paragraph._element.xpath(".//w:r")]


def to_float(value):
    """Profile number -> float, tolerating the Turkish decimal comma ("2,5" -> 2.5).

    Returns None when the value cannot be read as a number, so the caller can warn
    and skip that one field instead of crashing the whole run. Author-guideline
    profiles are written by an agent from Turkish sources, where "2,5" is normal.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip().replace(",", "."))
    except (ValueError, AttributeError):
        return None


def iter_tables(doc):
    """Top-level and nested tables."""
    def walk(container):
        for table in getattr(container, "tables", ()):
            yield table
            for row in table.rows:
                for cell in row.cells:
                    yield from walk(cell)
    yield from walk(doc)


def count_drawings(doc):
    """Images in the body — inline AND anchored ('wrap text') alike.

    `Document.inline_shapes` sees only the inline ones, so a manuscript whose
    figures float would otherwise report zero figures.
    """
    body = doc.element.body
    drawings = body.xpath(".//w:drawing")
    anchored = body.xpath(".//w:drawing/wp:anchor")
    pict = body.xpath(".//w:pict")                  # legacy Word 97-2003 (VML) images
    return {
        "total": len(drawings) + len(pict),
        "inline": len(drawings) - len(anchored),
        "anchored": len(anchored),
        "legacy_vml": len(pict),
    }


def has_run_override(run, attr):
    """True when the run carries its own <w:rPr> child for `attr` (e.g. 'rFonts')."""
    rPr = run._element.find(qn("w:rPr"))
    return rPr is not None and rPr.find(qn("w:" + attr)) is not None
