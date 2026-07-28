# Publication Style Schema (Published Style)

This is the JSON structure the `journal-s-yayinstili` agent must produce and the `journalstyle` skill must read.
This file is **separate** from the official rule profile (`journalstyle-r-authorguidelines.md`): it holds not the official
rule but the **actual conventions observed from real articles published** in the journal.
Unknown/inaccessible fields are left `null`, not fabricated.

**Primary source = locally uploaded PDFs.** The user places sample articles from the target journal as PDFs into the
**workspace's** `yayinstili/<slug>/` folder (the slug is the same as `authorguidelines/<slug>.json`; workspace = the source
`.docx`'s folder, resolved by the skill with `journalstyle_workspace.py`). The agent extracts the style
**from these PDFs first** (with `journalstyle_extract_pdf_text.py`) and writes `style_source: "user-pdf"`;
if this folder is missing/empty, it falls back to a web search (`journal-auto`).

```json
{
  "journal_name": "The Spine Journal (TSJ)",
  "slug": "thespinejournal",
  "last_analyzed": "2026-07-11",
  "draft_topic_keywords": ["lumbar fusion", "spondylolisthesis", "PROMs"],
  "style_source": "user-pdf",
  "sample_selection": "locally uploaded PDFs (workspace: yayinstili/<slug>/); if none, web: topic-similar, last 5 years, open access",
  "sample_urls": [
    "2025 Ardelt. Risk factors ... The Spine Journal.pdf",
    "2025 Huybregts. Hounsfield unit ... The Spine Journal.pdf"
  ],
  "sample_n": 5,
  "structure": {
    "tables_per_article": {"median": 3, "range": [1, 6]},
    "table_numbering": "Table 1, Table 2 ... (order of appearance in the text)",
    "table_caption_position": "above-table",
    "table_notes_style": "footnote below the table, with symbols (*, †, ‡)",
    "figures_per_article": {"median": 2, "range": [0, 5]},
    "figure_numbering": "Figure 1, Figure 2 ...",
    "figure_panel_labeling": "A, B, C subpanels",
    "figure_caption_position": "below-figure",
    "caption_format": "'Table N.' + bold short heading + descriptive sentence; abbreviations in the footnote (RULE — NOT verbatim caption text)",
    "reference_count": {"median": 35, "range": [20, 60]},
    "de_facto_headings": ["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
    "section_order": ["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
    "abstract_de_facto": {
      "structured": true,
      "heading_count": 4,
      "headings": ["Background", "Methods", "Results", "Conclusions"],
      "word_count": {"median": 248, "range": [220, 265]}
    },
    "article_word_count": {"median": 3200, "range": [2600, 4100]}
  },
  "text_style": {
    "tense_by_section": {
      "introduction": "present+past",
      "methods": "past",
      "results": "past",
      "discussion": "present+past (general truths present)"
    },
    "passive_voice_ratio": "~60% passive (dense in Methods)",
    "first_person_usage": "'we' is used (Methods & Discussion)",
    "avg_sentence_length": {"median_words": 22, "range": [18, 28]},
    "in_text_citation_format": "numbered superscript [1,2]",
    "citation_density": "~1 citation / 2-3 sentences; dense in Introduction and Discussion",
    "stats_presentation": "mean ± SD, 95% CI in parentheses, p<0.001 format"
  },
  "notes": "Access/paywall restrictions, fallback info if no topic-similar sample was found, and conflicts with the official rule are written here as free text."
}
```

## Filling rules

- `style_source`:
  - `"user-pdf"` = the style was extracted from the **locally uploaded PDFs** under the workspace's `yayinstili/<slug>/`
    (primary, default path).
  - `"journal-auto"` = there were no local PDFs, fell back to **web** auto-selection from the journal (backup).
  - `"user-supplied"` = only the single article given via `user_reference_article`.
  - `"both"` = local PDF/user article + web journal samples together.
- For each numeric metric (`tables_per_article`, `figures_per_article`, `reference_count`), `sample_n` reflects
  how many sources it was computed from; the examined sources are listed under `sample_urls`
  — **in local PDFs, filenames instead of URLs** (if a user article was given,
  it is included in this list too). That the source is a local PDF is noted in `notes`.
- Inaccessible (paywall) fields or fields that cannot be reliably extracted from a single sample are left `null` and
  the reason is written into `notes` — no guesses are produced.
- `avg_sentence_length` and `passive_voice_ratio` are computed only if **full text** was fetched;
  with abstract-only access, the relevant field is left `null` and the reason written into `notes`.
- `article_word_count` is an **observation** of the de-facto publication length, not the word LIMIT; the official limit
  is in `<slug>.json`. `in_text_citation_format` is the observed citation form; the official `citation_style`
  is again in `<slug>.json`, and if they conflict it is noted in `notes`.
- **Copyright:** **no sentence, caption, or abstract text is copied verbatim** from the sample articles into the profile;
  only numeric metrics and structural patterns **expressed as a rule** are kept
  (e.g. `caption_format` is a format rule, not the actual caption text).
- When the schema grows, new fields not present in old cached JSONs are treated as `null`; the next
  run fills them.
- This file does **not override** the `formatting`/`figures_tables` rules in the official profile (`<slug>.json`);
  if it conflicts with them, the conflict is noted in `notes` (the observation may come from the typeset final form).
- `last_analyzed` is updated on every run; the skill checks freshness and, if needed, asks the user whether to
  re-run.

## What to measure

Every observation is a **measurable parameter**, never a vague phrase ("suitable style", "academic
tone" are not observations). The fields above fall into two groups:

- **`structure`** — table and figure counts (median/range), their numbering style, caption position,
  table footnote style, multi-panel labeling, `caption_format` (the caption **sentence pattern as a
  rule**, never the actual caption text), reference count, the de-facto headings and their order, the
  abstract's de-facto structure, and `article_word_count` (the observed publication length — an
  observation, not the word LIMIT, which lives in `<slug>.json`).
- **`text_style`** — tense by section, passive/active ratio, whether "we" is used,
  average sentence length, the observed in-text citation form, citation density (roughly one citation
  per how many sentences, and which section is dense), and statistics presentation.

**Measurement-access rule:** `avg_sentence_length` and `passive_voice_ratio` need **full text**.
Locally uploaded PDFs are full text, so they can be computed; when only an abstract is reachable in
the web backup, leave the field `null` and write the reason in `notes`.

## Call procedure

This procedure is the **single** source for both callers (`journalstyle` step 2.5, `journalwriter`
§3c). Neither SKILL.md repeats it; they point here.

**1. Cache first.** Read `<yayinstili_dir>/<slug>.yayinstili.json` (`yayinstili_dir` comes from
`journalstyle_workspace.py`; the profile sits beside the sample PDFs it was measured from).
- Present and `last_analyzed` newer than 6 months → use it as the style frame, **do not call the
  agent**. Writing several sections of one manuscript must not re-analyze the same journal.
- Present but older than 6 months → ask the user: use the cached analysis, or re-analyze?
- Absent → continue to step 2.

**2. Call the agent.** Pass `journal-s-yayinstili`: journal name · slug · article type (if any) · the
official profile (`<slug>.json`) · the source draft's topic/keywords (from title/abstract/keywords) ·
`yayinstili_slug_dir` · `yayinstili_dir` · `user_reference_article` if the user named a specific sample
article (file/URL/DOI).

**3. What comes back.** The agent **writes `<yayinstili_dir>/<slug>.yayinstili.json` itself** and
returns the style summary the caller uses directly (see its "Output Format"): dominant tense/voice,
citation density, de-facto headings, statistics presentation, table/figure medians, `style_source`,
and the fields left `null` with their reason. The raw JSON body is not returned — it is on disk.

**Why the agent writes here** (unlike `<slug>.json`): this is measurement, not a rule. There is no
user decision to gate it, so the agent stays single-shot and its `Write` is genuinely used. The
observation never overrides the official profile.
