<!-- Adapted from k-dense-ai/scientific-agent-skills/skills/pptx-posters — references/poster_design_principles.md + references/poster_layout_design.md + references/poster_content_guide.md + assets/poster_quality_checklist.md, MIT, K-Dense Inc. Condensed; the manifest schema is in journalsunum-r-postermanifest.md. -->

# Poster — content rules, dimensions, design, release checklist

A poster is **not a deck**: one page, read unattended at 1–2 metres, printed once at a fixed
physical size, and bound to organiser and printer rules that vary by event. This file is
read by `journalsunum-s-poster`; the manifest it renders from is specified in
`journalsunum-r-postermanifest.md`.

## 1. Requirements outrank conventions

There is no universal poster size, orientation, grid, body font, margin, DPI or column
count. Before any layout, record — each with an exact source ID in the manifest:

- **organiser rule:** maximum width × height, orientation, delivery format (PDF / PPTX /
  both), file naming, deadline;
- **printer rule:** trim size, bleed per edge, safe margin inside trim, accepted colour mode
  (RGB / CMYK / printer-managed), whether uniform scaling is allowed, proof workflow.

Two dated examples of how much they differ: CSCW 2026 allotted 48 × 48 in and recommended
≤ 45 in a side; IEEE DSC 2025 required an A1 space (84.1 × 59.4 cm). A congress board size,
a maximum poster size, a submission-document format and the physical print size can all be
different rules. Generic advice is a labelled *heuristic*, never promoted to a requirement.

## 2. Six geometry concepts — keep them apart

1. **Trim** — finished size after cutting.
2. **Bleed** — artwork beyond each trim edge, if the printer requires it.
3. **Artboard** = trim + 2 × bleed.
4. **Safe margin** — inset inside the trim edge for non-bleed content.
5. **PowerPoint canvas** — the slide size stored in the PPTX; each dimension **1–56 in**
   (Microsoft's current limit), all slides the same size.
6. **Print scale** — uniform conversion canvas → artboard.

```
scale_x = artboard_width / canvas_width ;  scale_y = artboard_height / canvas_height ;  scale_x == scale_y
final_font_pt      = design_font_pt × scale
final_placed_in    = design_in × scale
effective_dpi      = image_px / final_placed_in      (compute for width AND height; report the lower)
canvas safe inset  = (bleed + safe_margin) / scale
```

If the artboard exceeds 56 in on an edge, use a proportional smaller canvas, record the
scale, and confirm the printer permits scaling. Never scale width and height differently.
Native text never enters the bleed; only intentional imagery may.

**A 70 × 100 cm portrait poster** (a common Turkish-congress size): trim 27.56 × 39.37 in,
fits the canvas directly at scale 1.0; with 3 mm bleed the artboard is 28.15 × 39.96 in.

## 3. Font size means final-output size

PowerPoint stores design points; the printer scales them. Microsoft's 18 pt recommendation
is for *slides*, not a poster minimum. Viewing distance, typeface, substrate, lighting and
the organiser can require larger. The manifest therefore carries a final-output minimum
and a labelled basis (`heuristic` / `source_specific` / `conference_requirement` /
`printer_requirement`). Practical heuristics at 1–2 m: title 72–120 pt, section headings
36–48 pt, body 24–32 pt, captions/references 18–24 pt — all *final*.

Fonts are requests, not guarantees: confirm every face is installed on the export
workstation, check substitution and glyphs (Turkish characters, Greek, symbols) in
PowerPoint and in the PDF, and decide embedding with the printer. The generator embeds
nothing.

## 4. Content is source-bound and author-controlled

The generator renders approved manifest text. It does not research, infer, summarise or
"improve" a claim. Never invent poster text, citations, numbers, author details,
affiliations, funding, image licences or QR targets. If a source or approval is missing,
stop; keep the manifest in `draft`.

**Evidence packet the skill collects before the manifest:** accepted abstract or approved
summary · exact title, author order, affiliations, contact · final tables/figures with
captions, units, n, statistics, uncertainty · bibliography or exact identifiers · funding /
conflict / ethics / registration statements · optional logos and images with provenance and
permission · organiser and printer instructions · exact QR target and the visible fallback
URL. Each becomes a `sources[]` record with a unique ID; `author_verified: true` means a
human checked it.

**Selecting content:** what question should the viewer understand? which exact result
carries the take-home? which method detail is needed to interpret it? which limitation
prevents overstatement? what should the viewer do next? Typical sections — context,
objective, methods, results, limitations, conclusions, references, acknowledgements,
contact — included only when supported.

**Preserving meaning when shortening:** keep direction, magnitude, units, denominators,
uncertainty and qualifiers; association is not causation; keep null results that prevent
a misleading summary; keep PICO and time frame; no significance language the source lacks;
define acronyms; citation labels stay synchronised with the bibliography. An agent may
propose shorter wording; the author approves the exact text and the content hash renews.

**Citations:** copied from the author's verified bibliography — in this package the strings
come from `journal-s-zotero`; identifiers exact (DOI case included). A QR is never the only
way to reach essential content or the full reference list.

## 5. Visual hierarchy and accessibility

- A small, consistent set of text roles; left-aligned body; evidence, caption and
  interpretation grouped spatially; spacing, alignment, size and weight before decoration;
  no unexplained icons, no dense backgrounds, no text over uncontrolled imagery.
- Confirm the actual reading order; the manifest lists elements in contiguous
  `reading_order`, the title first, and the generator adds shapes in that order.
- **Text contrast** (WCAG 2.2 SC 1.4.3 used as the design target): 4.5:1 normal text; 3:1
  for large text (≥ 18 pt final, or ≥ 14 pt bold). **Non-text** graphical parts 3:1
  (SC 1.4.11). Colour is never the only encoding (SC 1.4.1): label series directly, add
  shape/pattern/line style, keep distinctions in grayscale. The palette checker reports
  ratios; it does not certify colour-vision accessibility.
- Palettes: ColorBrewer (qualitative / sequential / diverging, colour-blind-safe filters) or
  Paul Tol's schemes; test the actual figure on the actual background.
- **Alt text** for every picture (purpose and essential conclusion, not every pixel; no
  "image of"); important words as native text, never only inside a raster. A complex figure
  gets a source-bound native long description that follows it in reading order.
- QR codes: the exact `https://` target in visible fallback text, alt text stating the
  destination, a square box, tested on multiple devices after printing.

## 6. Layout

Choose the grid after content, orientation, language and dimensions are known. One broad
column for a single narrative; two columns for comparisons or small formats; three or more
shorten lines on wide canvases at the cost of navigation. No column count is inherently
"standard". Every element is an explicit rectangle on the canvas; images are placed with
`contain` (aspect preserved, centred, never cropped or stretched — a needed crop is a new
approved asset).

The layout checker reports shapes outside the slide, bounding-box intersections, text
without explicit size, text below the final minimum, and reading-order mismatches. Bounding
boxes are conservative; a clean report still does not prove there is no rendered overflow
or font substitution — inspect in PowerPoint and in the PDF.

## 7. Images and colour mode

Effective DPI = pixels / final placed inches, never file metadata. Only local PNG/JPEG,
hashed, with provenance and licence, EXIF/XMP/comments stripped offline before hashing.
PowerPoint may compress pictures on export — check the export settings and the PDF.
PowerPoint is an RGB workflow: if the printer needs CMYK, print-readiness waits for a
printer-approved conversion and proof; never label a native PowerPoint PDF as CMYK.

## 8. Export

Export with Standard / high print quality, never Minimum size. With PowerPoint installed the
agent exports through the plugin-root bridge (`scripts/office_kopru.py pdf` — PowerPoint's
`SaveCopyAs` as PDF, standard quality, into `<outputs_dir>/<stem>_poster.pdf`); otherwise the
export plan's `manual_actions` are the author's steps. Either way, verify the PDF independently:
page size = artboard, orientation, one page, fonts and glyphs, clipping, image resampling,
tags / reading order / alt text / language, colour proof, organiser naming and size limits.
If anyone later changes the slide size in PowerPoint, treat it as a layout change: re-check
scale, fonts, DPI, bounds; renew approval; re-export; re-proof.

## 9. Release checklist (condensed — the agent walks it before saying "ready")

1. **Requirements and approval** — organiser and printer rules recorded with source IDs; no
   generic size substituted; every claim/number/citation/author/logo/figure/licence has a
   source ID; every source `author_verified`, every element and asset `author_approved`; no
   placeholder remains; the author reviewed the canonical content hash after the last edit.
2. **Safe generation** — exact pinned dependencies; local assets only; hashes match; no
   template, remote image, API key or network; a new output path; `.pptx`, never `.pptm`.
3. **Package security** — no traversal / symlink / encryption / oversized entries; macro-free
   content type; no VBA, ActiveX, OLE, embedded or external-link parts; no external
   relationships; internal targets resolve; inspected as ZIP/XML, never opened by the script.
4. **Dimensions** — canvas within 1–56 in; trim, bleed and artboard recorded separately;
   canvas and artboard share the aspect ratio; uniform scale recorded; non-bleed content
   inside the safe margin; a proof confirms trim and bleed.
5. **Layout and typography** — nothing out of bounds; every overlap removed or documented;
   no overflow or auto-shrink; fonts assessed at final output with a labelled basis; faces
   installed; substitution and glyphs checked; hierarchy legible on a reduced-scale proof.
6. **Images** — effective DPI meets the labelled threshold; aspect preserved; no resampling
   artefacts in the PDF; provenance, licence and alt text in the inventory; metadata stripped.
7. **Colour and graphics** — text pairs 4.5:1 / 3:1 as declared; non-text 3:1; nothing by
   colour alone; palette suited to data type; a colour proof from the printer.
8. **PowerPoint accessibility** — alt text on every picture; long descriptions where needed;
   important text native; title is the native title placeholder; Reading Order pane matches;
   Accessibility Checker clean; keyboard and screen-reader pass; QR fallback text present
   and the printed code tested. *Manual:* the Checker has no automation API — the bridge can
   only open the file with the pane showing (`office_kopru.py open --pane accessibility`);
   the result is the author's reading.
9. **Export and print** — Standard quality; no media added after generation; PDF page size
   equals the artboard; PDF checked independently; RGB vs CMYK settled; organiser and
   printer rules met. *The export itself is automatable through the bridge (§8); every
   verification bullet stays.*
10. **Sign-off** — author approved content and citations; accessibility reviewer signed;
    printer approved dimensions and colour; manifest, PPTX hash, inventory, reports, PDF and
    proof retained together. Any later change restarts the checklist.

Automation finds technical defects. It cannot certify accessibility or scientific accuracy;
those are the author's and the reviewer's signatures.
