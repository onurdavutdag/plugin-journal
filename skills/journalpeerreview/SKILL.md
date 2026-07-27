---
name: journalpeerreview
description: >-
  Bu skill, bir makaleyi/taslağı GÖNDERİM ÖNCESİ hakem (peer reviewer) gözüyle sistematik ve eleştirel
  değerlendirmek için kullanılmalıdır: metodoloji, istatistik, çalışma tasarımı, tekrarlanabilirlik, etik, şekil/veri
  bütünlüğü ve raporlama standartlarına uyum. Yapılandırılmış bir hakem raporu üretir (özet +
  karar önerisi + major/minor yorumlar + yazara sorular). Tetikleyiciler: "hakem değerlendirmesi
  yap", "makaleyi/taslağı hakem gözüyle eleştir", "reviewer gözünden bak", "gönderim öncesi
  eleştirel değerlendirme", "peer review yap", "reviewer 2 gibi bak", "bu makale yayına hazır mı".
  Bu skill YALNIZCA DEĞERLENDİRİR; metni yazmaz (journalwriter), biçimlemez (journalstyle), atıf/kaynakça
  düzenlemez (journal-s-zotero), kaynak eklemez (journalresearch) — bulduğu sorunları ilgili takım üyesine devreder.
version: 1.10.1
---

# journalpeerreview — Critical Scientific Evaluation and Peer Review

Evaluate a scientific manuscript systematically from a reviewer's view. Examine methodology,
statistics, design, reproducibility, ethics, and reporting standards constructively but rigorously.
Goal: strengthen the author's manuscript **before submission**; catch blind spots and rejection risks
in advance.

## When to use

- Evaluating a manuscript/draft to be submitted to a journal from a reviewer's view
- Auditing the soundness of methodology and experimental design
- Examining the quality of statistical analysis and reporting
- Checking reproducibility, data/code availability
- Verifying compliance with reporting guidelines (CONSORT, STROBE, PRISMA, CARE, STARD, ARRIVE)
- Checking figure/table quality and image integrity
- Giving constructive, actionable reviewer feedback on a draft

## Single-ownership rule — the reviewer is ADVISORY ONLY

**This skill evaluates, it does NOT fix.** It **never touches** the manuscript file (docx/citation/format/text).
For every issue it finds, it **hands the solution off to the responsible team member** and writes this clearly in the report:

| Finding type | Responsible (handed off to) |
|---|---|
| Unsupported claim / missing / weak citation | **journalresearch** (finds a real DOI/PMID source) + **journalwriter** (works it into the text) |
| In-text citation / bibliography format, numbering, style | **journal-s-zotero** (agent, sole authority) |
| Mechanical format (font, size, margin), section order, word limit | **journalstyle** |
| Section writing/structure weakness (Introduction gap, Discussion flow, Abstract) | **journalwriter** |
| A case where analysis/statistics need to be redone | the user / the **istatistik-profesoru** skill (global, outside the plugin) |

The reviewer does **not do** these jobs itself; it only says "there is this issue → this skill solves it".
The `Write` permission is **only** for creating a separate *evaluation report* file — not for editing the manuscript.

## Core rule — no fabrication (inherited from journalresearch)

**Do not fabricate a non-existent error, missing citation, or non-compliance.** Every finding must be based
on what is **actually** seen in the text/data; do not accuse on the assumption "it is probably missing". When
a point is uncertain, write it as a "question to the author", do not present it as a major gap. Likewise, do not
fabricate the necessity of a source/standard — show the truly applicable guideline.

## Input and language

- **Input:** the manuscript/draft to evaluate (`.docx`/`.pdf`/`.md`), the target journal name if any,
  the study type (RCT / cohort / case-control / cross-sectional / diagnostic / case report / review).
- **Language:** write the report **in the language of the source text** (Turkish manuscript → Turkish report; English → English).
  If unclear, assume Turkish.
- Read a docx with `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/extract_docx_structure.py`,
  and a PDF with Read (`pages`) or `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/extract_pdf_text.py`.

## Calibrate the target journal's expectation (in-plugin profile)

There are no external "venue-templates"; get the target journal's expectation from the **journalstyle profile system**.
Profiles are no longer inside the plugin but **in the study's workspace** (the folder of the manuscript reviewed),
under `journal-profiles/`. Resolve the workspace:
`PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/workspace.py" "<manuscript.docx>"`
then Glob the returned `<profiles_dir>` folder; find the profile for the target journal.
There may be two files (the plain slug convention):

- Official rule profile: `<slug>.json` (e.g. `thespinejournal.json`) — word limit, required
  sections, citation style, IMRaD requirements.
- De-facto publication style / reviewer expectation profile (if any): `<slug>.yayinstili.json` — typical table/figure count, reference count,
  statistics presentation, tense/voice.

If a profile exists, calibrate the evaluation to it (e.g. "the journal has a median of 3 tables, the draft has 7 →
a simplification comment"). **If there is no profile**, write in the report "the target journal profile was not found,
evaluated by general standards"; optionally suggest the user produce a profile with `journalstyle`'s
`journal-s-authorguidelines` subagent. Do **not fabricate** a profile rule.

## Peer review flow (7 stages)

Apply the stages, deepening them by article type and discipline.

### Stage 1 — Initial assessment
High level: the central research question/hypothesis, main findings, scientific soundness and importance,
suitability for the target journal, whether there is a major flaw that blocks publication. **Output:** a 2–3 sentence summary impression.

### Stage 2 — Section-by-section review
- **Title/Abstract:** accuracy (does it reflect the content), clarity, completeness, accessibility to a broad reader.
- **Introduction:** current/adequate background, rationale, novelty, relevant literature, a clear aim/hypothesis.
- **Methods:** reproducibility (can someone else replicate it), suitability, sufficient detail
  (protocol/reagent/device/parameter), ethics approval & consent & data handling, appropriate statistics, controls.
  Verify: sample size & power analysis, randomization/blinding, inclusion/exclusion criteria,
  software versions, multiple-comparison correction.
- **Results:** logical presentation, figure/table labeling, effect size + CI + p, avoidance of
  over-interpretation, completeness including negative results, raw/summary data.
- **Discussion:** conclusion supported by the data, discussion of limitations, placement in the literature,
  separation of speculation from data, importance, future directions. **Red flags:** an inflated conclusion,
  ignoring contradicting evidence, causation from correlation, a mechanism claim without mechanism evidence.
- **References:** are the key articles present, currency, balance of opposing views, accuracy, excessive self-citation.
  (If it is a citation **format/number** issue → **journal-s-zotero**; if it is a missing **source** issue → **journalresearch**.)

### Stage 3 — Methodological and statistical rigor
**Read** `references/journalpeerreview-r-common-issues.md` and match against its items. Statistics:
assumptions (normality/independence/variance), effect size + p, multiple-test correction, CI,
power analysis, parametric/non-parametric choice, missing data, exploratory/confirmatory distinction. Design:
controls, biological/technical replication, confounders, randomization, blinding. Computational:
software version/parameter, code access, validation, batch correction. Audit per the user's **statistical
test symbol standard** (footnote) and **number/p format** rules (see below).

### Stage 4 — Reproducibility and transparency
Data availability (repository, accession no, justified restriction), code/material sharing,
protocol depth. **Reporting guideline compliance:** audit the guideline suited to the study type
against the **item-level Turkish package already in the plugin** — the source is here, do not fetch a separate file:

| Study type | Guideline | File |
|---|---|---|
| Randomized controlled | CONSORT | `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalwriter/references/journalwriter-s-danisman-r-guidelines/CONSORT.md` |
| Observational (cohort/case-control/cross-sectional) | STROBE | `.../STROBE.md` |
| Systematic review & meta-analysis | PRISMA | `.../PRISMA.md` |
| Case report/series | CARE | `.../CARE.md` |
| Diagnostic accuracy | STARD | `.../STARD.md` |
| Experimental animal | ARRIVE | `.../ARRIVE.md` |

Read the relevant file and compare the draft against the checklist items; mark missing items as major/minor.
(Genomics/proteomics/neuroimaging standards — MIAME, COBIDAS, etc. — are not needed in the medical/clinical
domain; if requested, direct to the official EQUATOR checklist, do not fabricate.)

### Stage 5 — Figures and data presentation
Quality: resolution, axis label+unit, defined error bar (SD/SEM/CI), significance notation,
color-blind-safe palette, scale bar. Integrity: image manipulation (duplication/splice), blot/gel
presentation, whether a representative visual is truly representative. Clarity: is it self-contained with the
figure legend, is the message clear, is there an unnecessary panel. (If the figure **caption position/format** is
a journal-style matter → **journalstyle**; the **visual content/integrity** is the reviewer's job.)

### Stage 6 — Ethics
Human: IRB/ethics approval, informed consent, protection of vulnerable groups, privacy, conflict of interest.
Animal: IACUC/equivalent approval, humane & justified procedure, 3R. Research integrity: suspicion of fabrication/falsification,
appropriate authorship, conflict/funding declaration, suspicion of plagiarism/duplicate publication.

### Stage 7 — Writing quality
Structure/organization, logical flow, transitions, clarity/brevity, jargon/abbreviation definition, grammar,
unnecessarily complex sentences, excessive passive voice, accessibility to a broad reader. (If a section **rewrite**
is needed, leave a suggestion note → **journalwriter**; the reviewer does not rewrite the text.)

## Peer review report structure

The report starts with the **provenance block** (see below), then:

1. **Summary evaluation (1–2 paragraphs):** a short synopsis of the research; a **decision recommendation**
   (accept / minor revision / major revision / reject); 2–3 strengths; 2–3 weaknesses; importance+soundness.
2. **Major comments (numbered):** issues that seriously affect validity/interpretability/importance.
   For each: (a) state the issue clearly, (b) why it is an issue, (c) suggest a concrete solution/additional analysis,
   (d) state whether it is required for publication, (e) **write the responsible team member** (journalresearch / journal-s-zotero / journalstyle / journalwriter).
3. **Minor comments (numbered):** clarity/completeness/presentation improvements. Location + issue + suggestion.
4. **Line-based comments (optional):** specific corrections referenced by page/section.
5. **Questions to the author:** methodological details needing clarification, results that seem contradictory,
   information missing for evaluation. (Put every uncertain point here instead of as a major.)

**Tone:** constructive, professional, collegial. Concrete and actionable. State the strengths too.
Focus on the science, not the person. Avoid: personal attack, sarcasm, vague criticism, imposing out-of-scope additional
experiments, presenting a personal preference as "best practice".

## Special notes by article type

- **Original research:** rigor, reproducibility, novelty, data-driven conclusion, complete methods/controls.
- **Review/meta-analysis:** literature coverage, search strategy, inclusion/exclusion, systematicity/bias,
  critical analysis (beyond summarizing), heterogeneity in a meta-analysis.
- **Methods paper:** validation & comparison with the existing method, protocol/code access, implementation detail.
- **Short report/letter:** expectation scaled to the brevity; the core finding must still be rigorous and important.
- **Preprint:** has not passed formal peer review; may be less polished, but the scientific validity criterion
  is the same; give constructive feedback for pre-submission improvement.
- **Presentation/slides (optional):** the focus is the docx manuscript. If a presentation PDF is to be evaluated, **do not
  read the PDF directly as text** (it misses visual format issues, gives a buffer error) — ask the user for the
  **visual (PNG/JPG) versions** of the slides, and review each slide visually; if the user does not provide visuals,
  skip this step. (The plugin has no automatic PDF→visual script.)

## Global output rules (the user's persistent rules)

- **Number/percentage/p-value format is language-dependent:** in a Turkish report the decimal is a **comma**, `%`
  is **before** the number, all numbers including p use a comma (e.g. `%73,5`, `p=0,028`, `p<0,001`). In an English report
  the decimal is a **period**, `%` is **after** (e.g. `73.5%`, `p=0.028`). Audit by this rule too.
- **Statistical test symbols:** in table/footnote auditing, apply the user's symbol standard
  (`*` Student's t, `**` Mann–Whitney U, `‡` Welch, `†` Fisher, `††` Pearson chi-square, `†††` McNemar,
  `§` paired t, `§§` Wilcoxon, `a` McNemar–Bowker). For a test not in the list, **do not use an existing
  symbol**; ask for the test name in words.
- **New file naming:** the produced report file is a NEW file → add the local date-time to the end of the
  name: `<name> YYYYMMDD HHMM.md` (e.g. `hakem_raporu 20260713 1042.md`). New file → **black** text
  (red only for updating an existing docx; the reviewer does not update the manuscript).
- The global CLAUDE.md PDF output rule applies: if a report is requested, a PDF may be produced alongside the `.md`.

## Report provenance (required)

Every report presented to the user starts, right under the title, with this provenance block; it lists the
references **actually** read in that job (no subagent → `—`; unused → `—`):

```
Skill: journalpeerreview
Subagent: —
References: <the ones read: journalpeerreview-r-common-issues.md / journalwriter-s-danisman-r-guidelines/<guideline>.md>
---
```

## Final checklist

Before finishing the report, verify: is the summary decision clear · are the major issues justified · are the suggestions
concrete & actionable · are the minors in the right category · were the statistics evaluated ·
were reproducibility/data access checked · was ethics verified · was figure/table integrity examined
· was writing quality checked · is the tone constructive · was each correction handed off to the right team member ·
was the manuscript file untouched · is the provenance block present.

## Reference files

- `references/journalpeerreview-r-common-issues.md` — 22 common methodology/statistics errors: definition,
  how to detect, what to suggest.
- Reused (not owned by this skill, do not touch): `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalwriter/references/journalwriter-s-danisman-r-guidelines/`
  (CONSORT/STROBE/PRISMA/CARE/STARD/ARRIVE item level) and the **workspace's** `journal-profiles/`
  (the `<slug>.json` / `<slug>.yayinstili.json` produced by journalstyle — resolved with `workspace.py`).
