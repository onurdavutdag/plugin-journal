<!-- Adapted from k-dense-ai/scientific-agent-skills/skills/pptx-posters — references/manifest_spec.md, MIT, K-Dense Inc. The template beside this file (journalsunum-poster-manifest-ornek.json) is upstream's assets/poster_manifest_template.json, unchanged and intentionally invalid. -->

# Poster manifest 2.0 — the only input the poster generator accepts

The manifest binds approved text and images, exact source IDs, local asset hashes and
licences, canvas and physical geometry, organiser and printer rules, accessibility
thresholds and their basis, reading order, and author approval to a canonical content
hash. Unknown keys, duplicate keys, non-finite numbers, remote paths, path escape,
unapproved fields, unresolved or unused sources, and common placeholders are **rejected** —
the validator refuses extensions rather than ignoring them.

`journalsunum-poster-manifest-ornek.json` is the template. It is intentionally invalid:
it holds `REPLACE_ME_*` tokens, false confirmations and draft approval so it cannot
produce a poster by accident. Copy it into the workspace's `outputs_dir`, then replace
every field with reviewed values. Asset paths are relative to the manifest's directory.

## Top level — exactly these keys

`schema_version` (`"2.0"`) · `document` · `canvas` · `physical_output` · `requirements` ·
`quality` · `palette` · `sources` · `assets` · `elements` · `approval`

## `document`

`id` (starts with a letter) · `title` (exact approved) · `subject` (core metadata) ·
`language` (BCP 47, e.g. `tr-TR`, `en-GB`) · `authors` (exact order) · `source_ids`.
Exactly one text element with role `title` must equal `document.title` verbatim and carry
`reading_order: 1`; it becomes the native slide-title placeholder.

## `canvas`

`width_in`, `height_in` — each 1–56 in · `background_color` — opaque `#RRGGBB`. These are
design dimensions, not automatically the trim size.

## `physical_output`

`trim_width_in`, `trim_height_in` · `bleed_in` (per edge) · `safe_margin_in` (inside trim) ·
`orientation` (`portrait` / `landscape` / `square`, matching the trim). Artboard = trim +
2 × bleed and must share the canvas aspect ratio.

## `requirements`

**`conference`** — `confirmed: true` · `source_id` (a source of kind `conference_rule`) ·
`max_width_in`, `max_height_in` · `orientation` (`portrait` / `landscape` / `square` /
`either`) · `required_delivery_format` (`PDF` / `PPTX` / `PDF_AND_PPTX` / `OTHER`) · `notes`.
The trim must fit.

**`printer`** — `confirmed: true` · `source_id` (kind `printer_rule`) · trim/bleed/margin
matching `physical_output` · `accepted_color_mode` (`RGB` / `CMYK` / `PRINTER_MANAGED`) ·
`scaling_allowed` · `notes`. If scaling is forbidden, canvas and artboard are 1:1. CMYK does
not block creating the RGB PPTX; it blocks the *print-ready* claim until a printer-approved
conversion and proof exist.

## `quality`

`minimum_font_pt_final` · `font_guidance_basis` · `font_guidance_source_id` ·
`minimum_raster_dpi_final` · `raster_dpi_basis` · `raster_dpi_source_id`.
Basis ∈ `heuristic` (source ID must be null) · `source_specific` · `conference_requirement`
· `printer_requirement` (each needs an exact source ID). Values apply at **final** output.

## `palette`

`colors` — stable IDs → opaque `#RRGGBB`. `contrast_pairs[]` — `id`, `foreground_color_id`,
`background_color_id`, `usage` (`normal_text` 4.5:1 · `large_text` 3:1, only for ≥ 18 pt
final or ≥ 14 pt bold · `non_text` 3:1). `data_series_redundant_encoding: true` — the
author's confirmation that colour is never the only encoding.

## `sources[]`

`id` · `kind` (author content, publication, dataset, asset licence, conference rule,
printer rule, institutional rule, other) · `citation` · `locator` (DOI, stable URL, local
record ID, figure/table number, page, dated author instruction) · `author_verified: true`.
Every source must be used; every referenced ID must exist. Scripts never dereference a
locator.

## `assets[]` (may be empty)

`id` · manifest-relative `path` (local PNG/JPEG only) · `role` (`figure` / `logo` /
`qr_code`) · lowercase SHA-256 · `source_id` · `license` · `provenance` · `alt_text` ·
`author_approved: true` · `qr_target` (null except QR, then an exact `https://` URL).
One record per file; every record must be placed; hashes must match; EXIF/XMP/comments are
rejected by the inventory — strip offline, rehash, re-approve.

## `elements[]`

Contiguous `reading_order` from 1, list order preserved. Every element: `id`, `type`,
`reading_order`, `x_in`, `y_in`, `width_in`, `height_in`, `source_ids`, `author_approved:
true`, `allow_in_bleed` (text: always false). All boxes on the canvas; non-bleed boxes inside
the mapped safe area.

**Text:** `role` (title, authors, affiliation, heading, body, caption, reference,
acknowledgement, contact, qr_fallback, other) · exact `text` · `font_size_pt_design` ·
`font_face` · `bold` · `align` · `vertical_align` · `contrast_pair_id` · optional
`line_color_id` · `line_width_pt` · `margin_in`. Font size is checked after scaling;
auto-shrink is disabled.

**Image:** `asset_id` · `fit: "contain"` · `fallback_text_element_id` (QR: an element of
role `qr_fallback` whose text contains the exact `qr_target`; otherwise null) ·
`long_description_element_id` (null when alt text + adjacent prose suffice; otherwise an
approved body/caption/other element that follows the image in reading order and cites every
source the image uses; null for QR).

## `approval`

Draft: `{"status":"draft","approved_by":null,"approved_at":null,"content_sha256":null}`.
After every non-approval field validates, obtain the hash (`--print-content-hash`), give
the exact manifest and hash to the author, then set `status: "approved"`, `approved_by`,
ISO-8601 `approved_at` with UTC offset, and the exact lowercase `content_sha256`. The hash
covers every top-level field except `approval` (canonical sorted UTF-8 JSON); **any** other
change invalidates approval.

## Validation modes and exit codes

- normal — reads and hashes assets, requires approval;
- `--structure-only` — no file reads; planning/audit only, never generation;
- `--print-content-hash` — permits draft approval, still rejects placeholders, unverified
  sources, unapproved elements, false requirements.

Exit 0 pass · 1 release-blocking finding · 2 invalid/unsafe input, missing dependency or
command error.

## How this package fills the manifest

The poster agent does not ask the user to hand-write JSON. The `journalsunum` skill
collects the evidence packet (title, authors, the approved abstract or summary, the exact
figures and their captions, reference strings from `journal-s-zotero`, the organiser's and
printer's rules, the QR target) and the agent writes the manifest from it, one `sources[]`
record per item. The approval hash is then returned to the skill, which asks the user; the
agent never approves on the author's behalf.
