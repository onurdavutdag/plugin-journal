<!-- Adapted from k-dense-ai/scientific-agent-skills/skills/scientific-slides — references/presentation_structure.md + references/presentation_workflow.md, MIT, K-Dense Inc. The "from manuscript to slides" mapping is this package's own addition. -->

# Structure — the narrative arc, and how a manuscript becomes a deck

This is the `journalsunum-s-danisman` agent's primary knowledge source. The parameters
(slide budgets per type and duration) are in `journalsunum-r-konusma.md`; design is in
`journalsunum-r-tasarim.md`.

## 1. The arc every scientific talk follows

1. **Hook** — 30 s to 1 min. A surprising number, a provocative question, a patient story, a
   visual puzzle, a contrast of paradigms, or scale ("affects X people, unsolved for Y years").
2. **Context** — 5–10 %. The research area and why it matters.
3. **Problem / gap** — 5–10 %. What is unknown or wrong.
4. **Approach** — 15–25 %. Your design and method, at the depth the audience needs.
5. **Results** — 40–50 %. The findings, shown, not told.
6. **Implications** — 15–20 %. What it means, how it sits with prior work, limitations.
7. **Closure** — 1–2 min. Take-home messages, and a final slide that invites discussion.

This mirrors IMRaD but is a *story*: each section answers the question the previous one
raised. The advisor's skeleton names, for every slide, which step of the arc it serves.

## 2. From a manuscript to a deck — the mapping

The usual raw material in this package is a manuscript (`journalwriter` output or the user's
own `.docx`), a thesis, or a results workbook, read through
`${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/hammadde_oku.py`. The mapping is not one section →
one slide; it is a selection.

| Manuscript part | Becomes | Rule |
|---|---|---|
| Title, authors, affiliations | Title slide | Title ≤ 15 words, specific ("X predicts Y in Z"), not generic. Congress name and date on the slide. |
| Abstract | nothing directly | The abstract is the *talk's* outline, not a slide. Use it to pick the 1–2 findings. |
| Introduction ¶1–2 (what we know) | Hook + Context, 1–2 slides | One visual, one number, 3–5 citations at most, shown as author-year on the slide. |
| Introduction ¶3 (what we don't know) | Gap slide, 1 slide | The single sentence that justifies the study. |
| Aim / hypothesis | Question slide, 1 slide | Verbatim from the manuscript, large. |
| Methods | 2–3 slides (congress) to 8–10 (defence) | Design → setting/participants → intervention/exposure → outcome → analysis. A flow diagram beats a paragraph; the CONSORT/STROBE diagram from the paper is the Methods slide. |
| Table 1 | one slide, simplified | Keep the rows the story needs; the full table is a backup slide. |
| Primary outcome | 2–3 slides | The figure first, the number with 95 % CI second, the statistic third. One message per slide. |
| Secondary outcomes | 1–2 slides each, or a summary slide | Only those the take-home depends on. |
| Discussion ¶1 (summary) | Interpretation slide | One sentence per finding. |
| Discussion ¶2–3 (prior work) | Comparison slide | 2–3 studies, a table or a forest-style layout, cited on the slide. |
| Limitations | Limitations slide | Always present, honest, 3–5 items; in a defence, comprehensive. |
| Conclusion | Take-home slide | 3–5 complete, memorable sentences — claims, not headings. |
| References | Reference strings on the slides that use them + optional closing list | Strings come from `journal-s-zotero` (see the skill); the deck never renders a bibliography by itself. |
| Acknowledgements, funding | Acknowledgement slide | 15–30 s. Grant numbers, collaborators, participants. |
| — | Final slide | "Questions?", contact, QR to the paper/preprint, one key visual. **Never** end on a references wall. |

**Selection test for every candidate slide:** does it serve one of the 1–3 core messages?
If not, it is a backup slide or nothing.

## 3. Structure by length — the skeletons the advisor returns

**10-minute congress** (10–12 slides): title · hook+context · gap · approach (1–2) · results
(4–5: primary, supporting, validation, optional extension) · interpretation (1–2) ·
conclusions · acknowledgements. Spend 40–50 % on results; keep 1–2 backup slides.

**15-minute congress** (15–18): title · hook · background (1–2) · gap · question · methods
(2–3: design/participants, procedure, analysis) · results (6–8: sample, finding 1, finding 2,
finding 3, optional sensitivity) · discussion (3–4: prior work, mechanism, limitations,
implications) · conclusions (1–2) · acknowledgements+questions.

**30-minute seminar / journal club** (25–30): opening (3–4, with an outline) · background
(4–5) · question · methods (5–6, with rationale and validation) · results (10–12, including
subgroup and sensitivity) · discussion (6–8) · conclusions (2) · acknowledgements.

**45-minute defence** (35–45): opening (4–5: hook, personal connection, outline) · big
picture (5–7) · prior work (4–5) · studies (8–10 slides each, with a transition slide between
that states what was learned and what remained open) · synthesis (5–7) · future directions
(2–3) · conclusions (2) · acknowledgements. Tell the arc *across* studies.

For talks over 20 minutes always include an **outline slide** (3–5 sections, visual, not a
bullet list) and return to it as the section divider.

## 4. Opening and closing

**Title slide:** specific title · name and credentials · affiliation with logo · congress and
date · optional QR. **Hook:** first 30–60 s; six patterns listed in §1.

**Conclusion:** the last 1–2 minutes are what is remembered. Use one of: 3–5 take-away
sentences; a call-back to the opening hook; the practical implication ("what does this mean
for the clinician"); a single integrating figure; 1–2 concrete next steps.

**Final slide (stays up during Q&A):** thank-you/questions · contact · QR · one visual.

## 5. Transitions and signposting

Section dividers in a consistent style, one word each. Verbal bridges: "now that we have
established X, here is how we measured Y"; "this raises the question…"; "coming back to our
original question…". For talks over 20 minutes, signpost: "three findings; first…".

## 6. The six-stage workflow the skill runs

1. **Planning** — type, duration, audience, venue, what happens after; then the 1–3 core
   messages, the 3–6 essential figures, the time per section. Citations needed for the hook
   and the discussion are identified *now*, before any slide exists.
2. **Design** — palette for the topic, fonts, 4–6 master layouts (`journalsunum-r-tasarim.md`).
3. **Content** — visual backbone first (every figure and diagram placed), minimal text second,
   speaker notes third. Text is the supporting role.
4. **Visual validation** — render, look at every slide as an image, fix, re-render (the
   render agent's loop).
5. **Practice** — the runs in `journalsunum-r-konusma.md` §7; cut what runs long.
6. **Final preparation** — copies on laptop/cloud/USB, a PDF backup, slide numbers, contact
   info, backup slides after the final slide.

## 7. Speaker notes

Every content slide carries notes: the one sentence the slide exists to say, the transition
into the next slide, and for a figure the "set-up / pattern / finding / statistic" sequence.
Notes are where detail lives that the slide must not show (exact p-values, the full CI list,
the caveat you will say aloud). Backup slides carry a note naming the question they answer.

## 8. Checklist before the outline goes to the user

- [ ] Clear arc hook → context → gap → approach → results → implications → closure
- [ ] Slide count fits the duration (~1/min) and 40–50 % of time is results
- [ ] Every slide serves one of the 1–3 core messages, or is marked backup
- [ ] Strong opening hook and a memorable conclusion; a final slide that invites discussion
- [ ] Section dividers / outline for talks over 20 min
- [ ] Backup slides listed with the question each answers
- [ ] Citations needed on slides identified (hook, comparison, mechanism) — to be resolved
      through `journal-s-zotero`, never typed from memory
