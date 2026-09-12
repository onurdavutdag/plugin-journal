#!/usr/bin/env python3
"""Measure a deck's slide text against the project's text-budget rules.

Library, not a CLI: `journalsunum_destedogrula.py` runs it. It reads
`ppt/slides/slideN.xml` as ZIP/XML — no python-pptx, no rendering, nothing opened in
PowerPoint — and turns the numeric rules of
`skills/journalsunum/references/journalsunum-r-tasarim.md` §2 into measured facts:
bullets per slide, words per bullet, body words per slide, line length, nesting depth,
explicit font sizes, a visual on the slide, a speaker note on the slide.

Two things this file deliberately does NOT do:

* It never guesses an inherited font size. A shape whose text carries no explicit `sz`
  (a template/theme deck) yields `FONT_SIZE_UNSPECIFIED`, never an assumed value — the
  same honesty contract `journalsunum_yerlesimdenetle.py` follows.
* It never calls `require_safe_pptx`. That is the one-slide poster profile: it forbids
  `ppt/notesSlides/`, hyperlinks, transitions and more than one slide, so every real deck
  fails it. Only the XML parts actually read here are preflighted (name safety, not
  encrypted, size and compression bounds); a deck's media is never opened, so its size is
  irrelevant.

The thresholds are a project heuristic from this package's own reference, not a standard;
every report says so in its `basis` block.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

from journalsunum_ortak import MAX_INPUT_BYTES, CliError, checked_input_file
from journalsunum_pptxokuyaz import (
    A_NS,
    MAX_COMPRESSION_RATIO,
    MAX_XML_BYTES,
    P_NS,
    PKG_REL_NS,
    R_NS,
    _parse_xml,
    _preflight_zip_directory,
    _resolve_internal_target,
    _shape_name,
    _shape_transform,
)

REPORT_SCHEMA_VERSION = "1.0"

SLIDE_PREFIX = "ppt/slides/slide"
NOTES_RELATIONSHIP = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
)

TITLE_PLACEHOLDERS = {"title", "ctrTitle"}
BODY_PLACEHOLDERS = {"body", "subTitle", "obj"}
# Chrome, never body text: footer, slide number, date.
CHROME_PLACEHOLDERS = {"ftr", "sldNum", "dt"}

DEFAULT_THRESHOLDS: dict[str, float] = {
    # journalsunum-r-tasarim.md §2 "Text budget"
    "bullets_target": 4,
    "bullets_ceiling": 6,
    "words_per_bullet_target": 8,
    "slide_words_ceiling": 36,
    "line_chars": 60,
    "max_level": 1,
    # §2 typography table + §7 ("body < 24 pt" is the recommended floor, not the minimum)
    "body_font_min": 18.0,
    "body_font_recommended": 24.0,
    "title_font_min": 28.0,
    "title_slide_font_min": 40.0,
}

BASIS = {
    "kind": "project_heuristic",
    "source": "skills/journalsunum/references/journalsunum-r-tasarim.md §2 + §7",
    "note": (
        "These numbers are this package's own guidance, not a published standard. "
        "Word counts split on whitespace; a hyphenated or apostrophised form counts as "
        "one word. Line length is a character count, not real text wrapping — it depends "
        "on font size and box width, so it is only ever a warning."
    ),
}


# --------------------------------------------------------------------------- helpers
def _slide_number(name: str) -> int:
    stem = name[len(SLIDE_PREFIX) : -len(".xml")]
    return int(stem) if stem.isdigit() else 0


def _slide_parts(archive: zipfile.ZipFile) -> list[str]:
    names = [
        n
        for n in archive.namelist()
        if n.startswith(SLIDE_PREFIX)
        and n.endswith(".xml")
        and _slide_number(n) > 0
    ]
    return sorted(names, key=_slide_number)


def _preflight_part(archive: zipfile.ZipFile, name: str) -> None:
    """Bound one XML part before reading it. Media parts are never read, never checked."""
    try:
        info = archive.getinfo(name)
    except KeyError as exc:
        raise CliError(f"package part {name} is missing") from exc
    if info.flag_bits & 0x1:
        raise CliError(f"package part {name} is encrypted")
    if info.file_size > MAX_XML_BYTES:
        raise CliError(
            f"XML part {name} is {info.file_size} bytes; limit is {MAX_XML_BYTES}"
        )
    if info.compress_size > 0:
        ratio = info.file_size / info.compress_size
        if ratio > MAX_COMPRESSION_RATIO:
            raise CliError(
                f"XML part {name} expands {ratio:.0f}x; limit is "
                f"{MAX_COMPRESSION_RATIO:.0f}x"
            )


def _read_xml(archive: zipfile.ZipFile, name: str):
    _preflight_part(archive, name)
    return _parse_xml(archive.read(name), location=name)


def _placeholder_type(shape) -> str | None:
    """The `a:ph@type` of a shape, or None when it is a plain text box."""
    nv = shape.find(f"{{{P_NS}}}nvSpPr")
    if nv is None:
        return None
    ph = nv.find(f"./{{{P_NS}}}nvPr/{{{P_NS}}}ph")
    if ph is None:
        return None
    # A placeholder with no `type` attribute is a body placeholder by OOXML default.
    return ph.attrib.get("type", "body")


def _paragraph_text(paragraph) -> str:
    parts = [node.text or "" for node in paragraph.iter(f"{{{A_NS}}}t")]
    return "".join(parts).strip()


def _paragraph_level(paragraph) -> int:
    props = paragraph.find(f"{{{A_NS}}}pPr")
    if props is None:
        return 0
    raw = props.attrib.get("lvl")
    if raw is None:
        return 0
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


def _paragraph_font_pt(paragraph) -> float | None:
    """The smallest explicit size in this paragraph; None when the theme decides."""
    sizes: list[float] = []
    for tag in ("rPr", "defRPr", "endParaRPr"):
        for node in paragraph.iter(f"{{{A_NS}}}{tag}"):
            raw = node.attrib.get("sz")
            if raw is None:
                continue
            try:
                sizes.append(int(raw) / 100.0)
            except ValueError:
                continue
    return min(sizes) if sizes else None


def _shape_paragraphs(shape) -> list:
    body = shape.find(f"{{{P_NS}}}txBody")
    if body is None:
        return []
    return list(body.findall(f"{{{A_NS}}}p"))


def _slide_height_emu(archive: zipfile.ZipFile) -> int | None:
    if "ppt/presentation.xml" not in archive.namelist():
        return None
    root = _read_xml(archive, "ppt/presentation.xml")
    size = root.find(f"{{{P_NS}}}sldSz")
    if size is None:
        return None
    try:
        return int(size.attrib["cy"])
    except (KeyError, ValueError):
        return None


def _notes_part(archive: zipfile.ZipFile, slide_part: str) -> str | None:
    directory, _, leaf = slide_part.rpartition("/")
    rels_name = f"{directory}/_rels/{leaf}.rels"
    if rels_name not in archive.namelist():
        return None
    root = _read_xml(archive, rels_name)
    for rel in root.findall(f"{{{PKG_REL_NS}}}Relationship"):
        if rel.attrib.get("Type") != NOTES_RELATIONSHIP:
            continue
        if (rel.attrib.get("TargetMode") or "Internal") != "Internal":
            continue
        target = rel.attrib.get("Target", "")
        try:
            resolved = _resolve_internal_target(rels_name, target)
        except CliError:
            return None
        return resolved if resolved in archive.namelist() else None
    return None


def _notes_text(archive: zipfile.ZipFile, part: str) -> str:
    root = _read_xml(archive, part)
    tree = root.find(f"{{{P_NS}}}cSld/{{{P_NS}}}spTree")
    if tree is None:
        return ""
    collected: list[str] = []
    for shape in tree.findall(f"{{{P_NS}}}sp"):
        # The slide-number placeholder on a notes page is not a speaker note.
        if _placeholder_type(shape) in CHROME_PLACEHOLDERS:
            continue
        for paragraph in _shape_paragraphs(shape):
            text = _paragraph_text(paragraph)
            if text:
                collected.append(text)
    return "\n".join(collected).strip()


def _finding(
    code: str,
    severity: str,
    slide: int,
    message: str,
    *,
    value: Any = None,
    threshold: Any = None,
    location: str | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "slide": slide,
        "message": message,
    }
    if value is not None:
        entry["value"] = value
    if threshold is not None:
        entry["threshold"] = threshold
    if location is not None:
        entry["location"] = location
    return entry


def resolve_thresholds(overrides: dict[str, Any] | None) -> dict[str, float]:
    """Merge caller overrides onto the §2 defaults, rejecting unknown or unusable keys."""
    thresholds = dict(DEFAULT_THRESHOLDS)
    if not overrides:
        return thresholds
    if not isinstance(overrides, dict):
        raise CliError("thresholds must be a JSON object")
    unknown = sorted(set(overrides) - set(DEFAULT_THRESHOLDS))
    if unknown:
        raise CliError(f"unknown threshold key(s): {', '.join(unknown)}")
    for key, raw in overrides.items():
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise CliError(f"threshold {key} must be a number")
        value = float(raw)
        if value != value or value in (float("inf"), float("-inf")) or value < 0:
            raise CliError(f"threshold {key} must be a finite, non-negative number")
        thresholds[key] = value
    return thresholds


# --------------------------------------------------------------------------- one slide
def _text_shapes(tree) -> list[dict[str, Any]]:
    """Every non-chrome text shape on the slide, with what is needed to classify it."""
    shapes: list[dict[str, Any]] = []
    for shape in tree.findall(f"{{{P_NS}}}sp"):
        kind = _placeholder_type(shape)
        if kind in CHROME_PLACEHOLDERS:
            continue
        paragraphs = [
            {
                "text": text,
                "level": _paragraph_level(paragraph),
                "font_pt": _paragraph_font_pt(paragraph),
            }
            for paragraph, text in (
                (p, _paragraph_text(p)) for p in _shape_paragraphs(shape)
            )
            if text
        ]
        if not paragraphs:
            continue
        box = _shape_transform(shape)
        shapes.append(
            {
                "placeholder": kind,
                "paragraphs": paragraphs,
                "y_emu": box[1] if box else None,
                "name": _shape_name(shape),
            }
        )
    return shapes


def _pick_title(
    shapes: list[dict[str, Any]], slide_height_emu: int | None
) -> tuple[dict[str, Any] | None, str]:
    """The title shape and how it was found.

    A placeholder wins outright. Failing that — and pptxgenjs, which this package's own
    generator uses, emits plain text boxes with no placeholder at all — the slide's
    topmost text shape is read as the title when it is a single line sitting in the upper
    half, the way a person reads it. Requiring it to be the topmost shape on the slide,
    not merely the topmost candidate, keeps a stray one-liner below a body box from being
    promoted. Without slide geometry nothing is inferred.
    """
    for shape in shapes:
        if shape["placeholder"] in TITLE_PLACEHOLDERS:
            return shape, "placeholder"
    if not slide_height_emu:
        return None, "none"
    positioned = [s for s in shapes if s["y_emu"] is not None]
    if not positioned:
        return None, "none"
    topmost = min(positioned, key=lambda s: s["y_emu"])
    if len(topmost["paragraphs"]) == 1 and topmost["y_emu"] <= slide_height_emu * 0.5:
        return topmost, "inferred"
    return None, "none"


def _measure_slide(
    archive: zipfile.ZipFile,
    part: str,
    number: int,
    slide_height_emu: int | None,
) -> dict[str, Any]:
    root = _read_xml(archive, part)
    tree = root.find(f"{{{P_NS}}}cSld/{{{P_NS}}}spTree")
    if tree is None:
        raise CliError(f"slide {number} has no shape tree")

    shapes = _text_shapes(tree)
    title_shape, title_source = _pick_title(shapes, slide_height_emu)

    font_unspecified = False
    title_text = ""
    title_font: float | None = None
    if title_shape is not None:
        title_text = " ".join(p["text"] for p in title_shape["paragraphs"])
        sizes = [
            p["font_pt"] for p in title_shape["paragraphs"] if p["font_pt"] is not None
        ]
        title_font = min(sizes) if sizes else None
        if title_font is None:
            font_unspecified = True

    bullets: list[dict[str, Any]] = []
    for shape in shapes:
        if shape is title_shape:
            continue
        for paragraph in shape["paragraphs"]:
            if paragraph["font_pt"] is None:
                font_unspecified = True
            bullets.append(
                {
                    "level": paragraph["level"],
                    "words": len(paragraph["text"].split()),
                    "chars": len(paragraph["text"]),
                    "font_pt": paragraph["font_pt"],
                    "text": paragraph["text"],
                }
            )

    visuals = len(tree.findall(f"{{{P_NS}}}pic")) + len(
        tree.findall(f"{{{P_NS}}}graphicFrame")
    )
    notes_part = _notes_part(archive, part)
    notes = _notes_text(archive, notes_part) if notes_part else ""
    body_fonts = [b["font_pt"] for b in bullets if b["font_pt"] is not None]

    # The opening slide is either marked as one (`ctrTitle`) or is simply the first
    # slide with nothing but a title and at most one line under it. Position matters:
    # a mid-deck section divider also carries only a title, and it is a content slide.
    placeholders = {s["placeholder"] for s in shapes if s["placeholder"]}
    is_title_slide = "ctrTitle" in placeholders or (
        number == 1 and visuals == 0 and len(bullets) <= 1
    )

    return {
        "slide": number,
        "part": part,
        "title": title_text,
        "title_words": len(title_text.split()),
        "title_font_pt": title_font,
        "title_source": title_source,
        "is_title_slide": is_title_slide,
        "bullets": bullets,
        "bullet_count": len(bullets),
        "body_words": sum(b["words"] for b in bullets),
        "max_line_chars": max((b["chars"] for b in bullets), default=0),
        "max_level": max((b["level"] for b in bullets), default=0),
        "has_visual": visuals > 0,
        "visual_count": visuals,
        "has_notes": bool(notes),
        "notes_words": len(notes.split()),
        "min_body_font_pt": min(body_fonts) if body_fonts else None,
        "font_unspecified": font_unspecified,
    }


# --------------------------------------------------------------------------- findings
def _judge_slide(slide: dict[str, Any], t: dict[str, float]) -> list[dict[str, Any]]:
    n = slide["slide"]
    out: list[dict[str, Any]] = []

    count = slide["bullet_count"]
    if count > t["bullets_ceiling"]:
        out.append(
            _finding(
                "BULLETS_OVER_CEILING",
                "issue",
                n,
                f"{count} bullets on one slide; the ceiling is "
                f"{int(t['bullets_ceiling'])}",
                value=count,
                threshold=int(t["bullets_ceiling"]),
            )
        )
    elif count > t["bullets_target"]:
        out.append(
            _finding(
                "BULLETS_OVER_TARGET",
                "warning",
                n,
                f"{count} bullets; the target is {int(t['bullets_target'])} or fewer",
                value=count,
                threshold=int(t["bullets_target"]),
            )
        )

    if slide["body_words"] > t["slide_words_ceiling"]:
        out.append(
            _finding(
                "SLIDE_WORDS_OVER_CEILING",
                "issue",
                n,
                f"{slide['body_words']} words of body text; the ceiling is "
                f"{int(t['slide_words_ceiling'])}",
                value=slide["body_words"],
                threshold=int(t["slide_words_ceiling"]),
            )
        )

    for index, bullet in enumerate(slide["bullets"], start=1):
        if bullet["words"] > t["words_per_bullet_target"]:
            out.append(
                _finding(
                    "WORDS_OVER_TARGET",
                    "warning",
                    n,
                    f"bullet {index} has {bullet['words']} words; the target is "
                    f"{int(t['words_per_bullet_target'])} or fewer",
                    value=bullet["words"],
                    threshold=int(t["words_per_bullet_target"]),
                    location=f"bullet {index}",
                )
            )
        if bullet["chars"] > t["line_chars"]:
            out.append(
                _finding(
                    "LINE_TOO_LONG",
                    "warning",
                    n,
                    f"bullet {index} is {bullet['chars']} characters; over "
                    f"{int(t['line_chars'])} it probably wraps to a second line",
                    value=bullet["chars"],
                    threshold=int(t["line_chars"]),
                    location=f"bullet {index}",
                )
            )
        if bullet["level"] > t["max_level"]:
            out.append(
                _finding(
                    "NESTING_TOO_DEEP",
                    "warning",
                    n,
                    f"bullet {index} is at indent level {bullet['level']}; keep nesting "
                    f"at {int(t['max_level'])} or less",
                    value=bullet["level"],
                    threshold=int(t["max_level"]),
                    location=f"bullet {index}",
                )
            )

    body_font = slide["min_body_font_pt"]
    if body_font is not None:
        if body_font < t["body_font_min"]:
            out.append(
                _finding(
                    "BODY_FONT_TOO_SMALL",
                    "issue",
                    n,
                    f"body text at {body_font:g} pt; the minimum is "
                    f"{t['body_font_min']:g} pt",
                    value=body_font,
                    threshold=t["body_font_min"],
                )
            )
        elif body_font < t["body_font_recommended"]:
            out.append(
                _finding(
                    "BODY_FONT_BELOW_RECOMMENDED",
                    "warning",
                    n,
                    f"body text at {body_font:g} pt; "
                    f"{t['body_font_recommended']:g} pt is the recommended floor",
                    value=body_font,
                    threshold=t["body_font_recommended"],
                )
            )

    title_font = slide["title_font_pt"]
    if title_font is not None and slide["title"]:
        floor = (
            t["title_slide_font_min"]
            if slide["is_title_slide"]
            else t["title_font_min"]
        )
        if title_font < floor:
            out.append(
                _finding(
                    "TITLE_FONT_TOO_SMALL",
                    "issue",
                    n,
                    f"title at {title_font:g} pt; the minimum is {floor:g} pt",
                    value=title_font,
                    threshold=floor,
                )
            )

    if slide["font_unspecified"]:
        out.append(
            _finding(
                "FONT_SIZE_UNSPECIFIED",
                "warning",
                n,
                "text has no explicit run or default font size; the layout or theme "
                "decides it, so the size must be checked by eye",
            )
        )

    if not slide["is_title_slide"]:
        if slide["bullet_count"] and not slide["has_visual"]:
            out.append(
                _finding(
                    "TEXT_ONLY_SLIDE",
                    "warning",
                    n,
                    "text with no figure, table or chart on the slide",
                )
            )
        if (slide["bullet_count"] or slide["has_visual"]) and not slide["has_notes"]:
            out.append(
                _finding(
                    "NO_SPEAKER_NOTES",
                    "warning",
                    n,
                    "content slide with no speaker note",
                )
            )

    return out


# --------------------------------------------------------------------------- entry
def measure_deck(
    value: str | Path, *, thresholds: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Measure every slide of a .pptx against the §2 text budget.

    Returns a JSON-ready report; raises CliError for anything that makes the deck
    unreadable (not a ZIP, missing part, oversized or malformed XML).
    """
    limits = resolve_thresholds(thresholds)
    path = checked_input_file(
        value, max_bytes=MAX_INPUT_BYTES, suffixes=(".pptx", ".potx", ".ppsx")
    )
    package_findings = _preflight_zip_directory(path)
    if package_findings:
        first = package_findings[0]
        raise CliError(f"{first['code']}: {first['message']}")

    slides: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as archive:
            parts = _slide_parts(archive)
            if not parts:
                raise CliError("package contains no ppt/slides/slideN.xml part")
            slide_height = _slide_height_emu(archive)
            for part in parts:
                measured = _measure_slide(
                    archive, part, _slide_number(part), slide_height
                )
                findings.extend(_judge_slide(measured, limits))
                # The bullet text itself stays out of the report: the agent already has
                # the outline, and a deck's full text would flood its context.
                for bullet in measured["bullets"]:
                    bullet.pop("text", None)
                slides.append(measured)
    except zipfile.BadZipFile as exc:
        raise CliError(f"file is not a readable ZIP package: {exc}") from exc

    issues = [f for f in findings if f["severity"] == "issue"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "path": str(path),
        "pass": not issues,
        "basis": BASIS,
        "thresholds": limits,
        "totals": {
            "slides": len(slides),
            "bullets": sum(s["bullet_count"] for s in slides),
            "body_words": sum(s["body_words"] for s in slides),
            "slides_with_notes": sum(1 for s in slides if s["has_notes"]),
            "slides_with_visual": sum(1 for s in slides if s["has_visual"]),
            "issues": len(issues),
            "warnings": len(warnings),
        },
        "slides": slides,
        "findings": findings,
        "inspection_method": "zip-xml-read-only",
    }


def summarize(report: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    """Fold a report into (info, warnings, issues) prose lines for the deck validator."""
    totals = report["totals"]
    info = [
        f"Text budget: {totals['bullets']} bullets, {totals['body_words']} body words "
        f"across {totals['slides']} slides",
        f"Speaker notes on {totals['slides_with_notes']}/{totals['slides']} slides; "
        f"a visual on {totals['slides_with_visual']}/{totals['slides']}",
    ]
    warnings = [
        f"Slide {f['slide']}: {f['message']} [{f['code']}]"
        for f in report["findings"]
        if f["severity"] == "warning"
    ]
    issues = [
        f"Slide {f['slide']}: {f['message']} [{f['code']}]"
        for f in report["findings"]
        if f["severity"] == "issue"
    ]
    return info, warnings, issues
