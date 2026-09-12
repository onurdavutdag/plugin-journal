<!-- Adapted from k-dense-ai/scientific-agent-skills/skills/scientific-slides — references/slide_design_principles.md + assets/powerpoint_design_guide.md + references/data_visualization_slides.md + references/common_pitfalls.md, MIT, K-Dense Inc. Merged and trimmed; the pptxgenjs specifics are left to the installed `pptx` skill and are not restated here. -->

# Slide design — invariants, typography, colour, layout, figures

Read by the render agent (`journalsunum-s-pptx`) before it writes a generator, and by the
advisor when it critiques an existing deck. Poster geometry is elsewhere
(`journalsunum-r-poster.md`); this file is about projected slides.

## 1. Three invariants

1. **One message per slide.** A slide with three graphs, eight bullets and two tables is
   three slides. Audiences read *or* listen, not both.
2. **Visual hierarchy.** Primary (largest, highest contrast) → secondary → tertiary. Size,
   colour, position (top-left / centre), weight — in that order, before any decoration.
3. **Consistency.** One font family (two at most), one palette of 3–5 colours, the same
   layout for the same kind of content, uniform margins. Build 4–6 master layouts and reuse
   them: title · section divider · content · full figure · two-column · closing.

**Anti-pattern to avoid at all cost:** all-bullet slides, black on white, default theme,
no figures, no citations — the "dry deck". Every content slide carries at least one strong
visual element; text supports, visuals lead.

## 2. Typography

| Element | Minimum | Recommended |
|---|---|---|
| Title-slide title | 40 pt | 44–54 pt |
| Slide title | 28 pt | 32–40 pt |
| Body | 18 pt | 24–28 pt |
| Figure labels | 18 pt | 18–24 pt |
| Caption / citation | 14 pt | 16–20 pt |
| Footer | 10 pt | 10–12 pt |

Sans-serif only (Arial, Calibri, Helvetica, Segoe UI); no script, decorative or condensed
faces; no italics or underline for emphasis (bold or colour instead); no ALL CAPS in body.
Left-align body text, centre titles and short key messages, never justify. Lines ≤ 50–60
characters; line spacing 1.2–1.5.

**Text budget:** 3–4 bullets of 4–8 words is the target. The ceiling is **6 bullets per
slide** and **36 words of body text per slide** (the 6×6 rule's product); a single bullet
over **8 words** is over target, and one that needs a second line — past roughly 60
characters — is a sentence, so cut it or move it to the notes. Fragments, not sentences;
parallel structure; key term in bold; nesting no deeper than one level.

These numbers are measured, not just advised: `journalsunum_destedogrula.py` reads the deck
and reports each slide against them (`BULLETS_OVER_CEILING`, `SLIDE_WORDS_OVER_CEILING`,
`WORDS_OVER_TARGET`, `LINE_TOO_LONG`, `NESTING_TOO_DEEP`, plus the font floors below). Target
overruns are warnings; a broken ceiling fails the run. They are this package's guidance, not
a published standard, and every report says so.

**The room test:** body text must be legible at six times the screen height. When in doubt,
larger.

## 3. Colour

Pick a palette for the **topic**, not the default theme: 3–5 colours, one or two accents.

| Use | Palette (hex) |
|---|---|
| Clinical / institutional | navy `1C3D5A` · grey `4A5568` · white; accent orange `E67E22` |
| Biomedical / life sciences | teal `0A9396` · coral `EE6C4D` · cream `F4F1DE`; accent burgundy `780000` |
| Neuroscience | deep purple `722880` · magenta `D72D51` · white |
| Large venue / high contrast | black or navy `003366` on white; white on dark grey `2D3748` |
| Data series (colour-blind safe) | blue `0173B2` · orange `DE8F05` · green `029E73` · magenta `CC78BC` |

Rules: contrast ≥ 4.5:1 (7:1 preferred — black/white 21:1, `003366`/white 12.6:1, white/`2D3748`
11.8:1); **never red–green as the only distinction** (≈ 8 % of men); pair colour with shape,
line style or a direct label; light backgrounds project best, dark ones need a dark room;
image backgrounds only on title and divider slides, with an overlay if text sits on them.
Colour carries a consistent meaning across the whole deck (the treatment arm is always the
same colour).

## 4. Layout

- **Margins** ≥ 5–10 % of the slide on every side; 40–50 % of the slide is white space on a
  good content slide. Aligned edges, an invisible grid, rule-of-thirds placement for the
  key element. Small misalignments read as carelessness.
- **Patterns:** title + content · two-column (text left, figure right) · full-figure (the
  key result) · text overlay (title, dividers) · grid (3–6 related items). Vary them; a deck
  of identical title-and-bullets slides is the dry deck.
- **No** decorative borders, 3D, shadows, clip-art, gradients that compete with content.
- **Animation** only for progressive disclosure (bullets one at a time, a figure built in
  layers, a process step by step); appear/fade/wipe, 0.2–0.3 s, on click; never fly/bounce/
  spin, never on every slide. Slide transitions: none, fade or push, uniform.
- **Slide numbers** on every content slide (the jury and the audience refer to them).

## 5. Figures for slides — simplify, do not replicate

A journal figure is dense for study; a slide figure is clear for five seconds.

- Remove minor gridlines, secondary axes, dense ticks, legends (label directly), and panels
  the current message does not need — split a 6-panel figure across 2–3 slides.
- Labels ≥ 18 pt, lines 2–4 pt, markers 8–12 pt, error bars 1.5–2 pt. Recreate the figure
  rather than pasting the journal version if its fonts are small (matplotlib
  `font.size = 18`, ggplot `base_size = 16`).
- Emphasise: the key series saturated, comparisons grey; annotate the finding on the plot
  ("34 % reduction, p < 0.001"); circle the region you will point at.
- Build complex figures progressively: baseline → group 1 → group 2 → highlight → annotation.
- Always on the plot: axis labels with units, n, what the error bars are (SD/SE/CI), the
  statistic. Bar charts start at zero; no 3D; no pie with > 5 categories; ≤ 4–5 lines per
  line plot; ≤ 6–8 groups per box plot (explain the box the first time); heatmaps with a
  sequential or diverging scale, never rainbow.
- Clinical staples: Kaplan–Meier with shaded CI, censor marks and HR on the plot; forest
  plots with the null line prominent; ROC with the diagonal and AUC (CI) on the plot,
  ≤ 3 curves.
- Tables: minimal, the comparison highlighted, never read cell by cell; the full table is a
  backup slide.

## 6. Accessibility and the recorded-talk test

High contrast, ≥ 18 pt, no meaning carried by colour alone, one concept per slide,
works in grayscale, readable on a phone. Say aloud what a figure shows ("notice the rising
trend") — the recording has no pointer.

## 7. Pitfall checklist (what the advisor's critique looks for)

**Content:** dry deck (no visuals, no citations) · everything from the paper · paragraphs
on slides · no narrative thread · results rushed, discussion long.
**Design:** default theme · text-only slides · body < 24 pt · low contrast · clutter · fonts
and colours changing slide to slide · no hierarchy.
**Timing:** not practised · no checkpoints · over time · conclusion skipped.
**Figures:** journal figure pasted as-is · illegible labels · chart junk · truncated axes ·
red–green · missing n / units / error definition · wrong chart type.

## 8. Design-first build order (what the render agent does)

1. Define the design system once: palette (from §3), fonts (from §2), layout constants.
2. Write reusable slide functions for the 4–6 layouts.
3. Place every visual first, then the minimal text, then speaker notes.
4. Measure the text budget (`journalsunum_destedogrula.py … --json`) before rendering: a
   broken ceiling is cheaper to fix in the generator than in the file.
5. Render → slide PNGs + labelled grid (real PowerPoint through the plugin-root
   `scripts/office_kopru.py render` when it is installed, else the `pptx` skill's
   LibreOffice `thumbnail.py`) → inspect every slide → fix in the generator, never by hand in
   the file → re-render, until the checklist in the agent body is clean.
6. Only then, and only for a deck the user wants polished: hand the file to PowerPoint
   Designer on screen (`office_kopru.py open --pane designer`); the user's picks are theirs,
   and a deck they saved is re-audited, never regenerated.
