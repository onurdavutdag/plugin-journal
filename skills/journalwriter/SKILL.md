---
name: journalwriter
description: >-
  Bu skill, bir akademik makalenin bir bölümünü (Tartışma/Discussion, Giriş/Introduction,
  Sonuç, Özet/Abstract vb.) hedef derginin yazar kurallarına ve kullanıcının kaynak
  şablonuna uygun şekilde YAZMAK için kullanılmalıdır. Tetikleyiciler; "tartışma bölümünü yaz",
  "giriş yaz", "sonuç bölümünü yaz", "bu dergi için özet yaz", "makale metni oluştur",
  "şu bölümü [dergi adı] stiline göre yaz" gibi ifadeler. Kullanıcı bir makale bölümü
  YAZDIRMAK istediğinde bu skill kullanılır (yalnızca biçimlendirme/format istediğinde
  journalstyle kullanılır — o farklıdır). Bu skill metni yazarken, kanıt gerektiren
  ve kullanıcının atıf vermediği her bilimsel/klinik iddia için OTOMATİK olarak `journalresearch`
  skill'ini çağırıp gerçek, doğrulanabilir alıntılar (DOI/PMID) ekler.
---

# Writer — Section Writing + Automatic Citation

Starting from the user's thesis/data and the template they sent, write a manuscript section
in the target journal's style. For every sentence in the text that needs evidence, trigger the
`journalresearch` skill and propose a **real** citation. Never a fabricated citation.

## Flow

### 1. Clarify the target
Get from the user (if it is already in the conversation, take it from there, do not ask again):
- **Which section?** (Discussion, Introduction, Conclusion, Abstract, Methods, etc.)
- **Target journal** (and article type: research article, case report, etc.)
- **Source file(s)**: the template/draft `.docx` the user sent, the thesis, and
  the Results/tables/statistics outputs (findings are required to write a Discussion).
- **Language**: the language of the source text (Turkish → write Turkish, English → write English). If unclear, ask.

### 2. Get the target journal profile (reuse the journalstyle infrastructure)
- **Resolve the workspace.** Profiles are no longer inside the plugin but kept **in the study's workspace**
  (the source `.docx`'s folder) under `journal-profiles/`. Resolve from the source `.docx` path:
  `PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/journalstyle_workspace.py" "<source.docx>" --slug <slug>`
  Use the `profiles_dir`, `yayinstili_slug_dir`, `authorguidelines_slug_dir` paths in the returned JSON.
- Get the profile by following **"Call procedure (checkpoint)"** in
  `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/references/journalstyle-r-authorguidelines.md`:
  cache check (6 months) → `journal-s-authorguidelines` call → user checkpoint → write. That section is
  the single description of the flow, shared with `journalstyle`; do not restate it here.
- **Red rule:** the agent returns the two finding sets **unmerged** and never writes `<slug>.json`.
  Per the user's decision **this skill** builds the final profile and caches it under `<profiles_dir>`.
- Use from the profile: `word_limit`, `section_order`, `abstract` rules,
  `citation_style` (Vancouver/APA/IEEE — pass this info to `journal-s-zotero`; that agent applies the citation format/bibliography,
  only the `{{zref:KEY}}` marker is written here), language and style hints.
- If a rule that cannot be verified is `null`, do not fabricate; warn the user.

### 3. Analyze the source and findings
- Examine the user's template/draft `.docx` with `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/journalstyle_extract_docx_structure.py`
  (current headings, tone, length, citation style). Match the writing style to it —
  imitate the user's voice, do not impose a generic academic tone.
- For the Discussion/Conclusion, take the findings (tables, p-values, effect sizes) from the source.
  Write the **number/percentage/p-value format per the user's global rule**: in Turkish, a comma
  and `%` before the number (e.g. `%73,5`, `p=0,028`); in English, a period and `%` after
  (e.g. `73.5%`, `p=0.028`). Footnote statistical tests with the user's symbol standard.

### 3b. Get writing guidance — call `journalwriter-s-danisman` automatically
**Before** writing the section, **call `journalwriter-s-danisman` automatically with the `Task` tool** (do not
wait for approval), in the same plugin. Pass it: which section (Introduction/Methods/Results/Discussion/
Abstract/Conclusion) · study type (RCT, cohort, case-control, cross-sectional, diagnostic, case report…) ·
PICO/hypothesis · the current draft if any.

What comes back is defined in the agent's **"Output Format"** — skeleton, content rules, reporting-guideline
items, common mistakes (plus a critique block when a draft was passed). Use that skeleton and those criteria
as the frame of the writing; do not restate the contract here. Note: `journalwriter-s-danisman` does **not
produce citations** — finding sources is `journalresearch`'s job in §5.

### 3c. Examine the publication/sample style — `journal-s-yayinstili`
**Before** writing the section, get the de-facto style by following **"Call procedure"** in
`${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/references/journalstyle-r-yayinstili.md`:
**first read `<profiles_dir>/<slug>.yayinstili.json`** — if it is fresh, use it and **do not call the
agent** (writing several sections of the same manuscript must not re-analyze the same journal). Only
when the file is missing — or, after asking the user, when it is older than 6 months — **call the
journal-s-yayinstili agent automatically with the `Task` tool** (do not wait for approval), in the same
plugin. Give it: target journal + slug + the source draft's topic/keywords + **workspace paths**
(`yayinstili_slug_dir`, `profiles_dir`) + **(if the user gave a specific sample article — "write per
this article", file/URL/DOI)** `user_reference_article`. The agent writes that file itself and returns
a style summary. Use the **de-facto style** as the style frame of the §4 writing (together with §3b's
advisor IMRaD skeleton):
- the dominant **tense/voice** (past/present, passive/active),
- **citation density** (how often in which section — tune the §5 research calls to this),
- the de-facto **section headings** and abstract structure,
- the **statistics presentation** (mean ± SD, 95% CI, p notation) — it does not conflict with the user's global
  number/p format rule, it is applied together with it.
Note: this agent only gives **observation**; it does not produce citations (that is §5 `journalresearch`'s job) and it does not write the text — this skill does.
If the user did not give a sample article, the agent auto-selects similar samples from the journal.

### 3d. Literature material from NotebookLM — call `journal-s-notebooklm` (Introduction and Discussion)
The user's literature pool in NotebookLM is the raw-material source for two jobs: the **background/gap**
paragraphs of the Introduction and the **comparison with the literature** paragraphs of the Discussion.
Writing any other section, skip this step entirely.

Follow **"Call procedure"** in `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/notebooklm-r-rehber.md`: when to
call · the brief to pass · what comes back · the two binding rules (content-never-a-citation, silent skip).
That section is the single description of the flow, shared with `journalresearch`; do not restate it here.

The returned material feeds two places: the Introduction's **problem → gap → aim** flow (§3b's advisor
skeleton) and the Discussion's **comparison with the literature** paragraphs, both written in §4.

### 4. Write the section
- Conform to the target journal's structure and word limit. Typical section logic:
  - **Introduction**: problem → gap → aim. Literature claims are dense here → citations are needed.
    Build the background and gap framing from §3d's NotebookLM output (what is known · where the studies
    disagree · which aspect is unstudied).
  - **Discussion**: main finding → comparison with the literature (supporting/contradicting) → mechanism
    → limitations → conclusion. Every "consistent with X / contrary to X" sentence needs a citation. In the
    comparison paragraphs, use §3d's NotebookLM output (which study found what,
    agreement/conflict direction).
  - **Abstract**: conform to the journal's `abstract` rules (word limit, whether structured).
- **Preserve, do not change** the citations the user already added.

### 5. Fetch citations automatically while writing — trigger the team member `journalresearch`
`journalresearch` is a team-member skill in the same plugin. Whenever a written paragraph contains a
claim needing evidence and the user gave no citation for that sentence, **call the `journalresearch` skill
with the Skill tool** (do not wait for approval). That skill:
- works four tiers in strict order: the references the user gave → the uploaded PDFs (while **always**
  scanning the user's fixed `pdflerim/` library, the PDF pool in the journalresearch skill's own folder)
  → the NotebookLM pool through `journal-s-notebooklm` → Consensus/PubMed,
- returns real, verifiable references with a DOI/PMID (does not fabricate),
- for each suggestion gives the evidence level + source + why-it-supports explanation,
- opens its output with the provenance block naming which subagent and which references it actually
  used — carry that block through when presenting the citations, do not strip it.

**Actually use the article `journalresearch` found/suggested in the text — not just listing it:**
- **Use the source's finding to support/shape the sentence.** Do not just attach a dry marker to the end of a
  sentence and move on; touch what the article found into the text — e.g. "Su et al. similarly reported a
  decrease in delirium incidence {{zref:KEY}}" or "contrary to this, study X found no difference".
  This way, the evidence research brought contributes to the argument of the writing.
- **Place the citation as a marker — do NOT set its format yourself.** At the exact point where the sentence is
  supported, write the canonical `{{zref:ITEMKEY}}` marker (for multiple sources in the same sentence, grouped
  `{{zref:KEY1;KEY2}}`). The marker grammar is in one place:
  `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-zref-protocol.md`.
  The in-text citation number/format (Vancouver `[1]`, APA
  author-year, etc.) and the bibliography list are **the `journal-s-zotero` agent's authority alone** — do not embed a raw
  number or `(Author, Year)`, do not **keep** a bibliography list. This authority is in no other component.
  - **Getting the keys — call #1 of the zotero contract.** Do not query the library yourself: send
    `journal-s-zotero` (Task) the list of sources to be cited (DOI/PMID/title) in one go. It matches them
    against the library, has the missing ones added through the add-methods flow (with the user's approval)
    and returns a `{source → ITEMKEY}` map plus whatever it could not resolve. One call for the whole
    section — the library listing stays inside the agent and never floods this conversation.
  - Write `{{zref:KEY}}` with the returned keys. For a source the agent could not resolve (and that the
    user does not want to add), leave the sentence without a marker and say so.
- `journal-s-zotero` does the **duplicate** (same DOI/PMID) check during render; use the same marker for the same source.
- If `journalresearch` says "no reliable evidence", do not fill the sentence with a **fabricated citation** — notify the user,
  suggest softening the sentence or providing a source.
- If the evidence is contradictory, reflect the uncertainty in the text (e.g. "the evidence is contradictory") and address both sides.

### 6. Present and report
- **Start the output with the provenance block** (see "Report provenance").
- Show the written section (with the citations as `{{zref:KEY}}` markers). In a separate part, list **each added
  citation's** research output format (Supported sentence · Reference · Why · Evidence level ·
  Source · Page/DOI/PMID) so the user can audit it.
- **Turning the citations into visible `[1]` and printing the bibliography is `journal-s-zotero`'s job.**
  **Render — call #2 of the zotero contract.** If the section goes into a `.docx`: write the text with its
  markers, then send `journal-s-zotero` (Task) the docx path + the style from the journal profile. It runs
  the render and returns the JSON report. Do **not** run the script yourself and do **not write the
  bibliography by hand.**
- Writing into a docx is subject to the global rule: **if an existing docx is updated, the added/changed text is red
  (RGB 255,0,0)**; a brand-new docx from scratch is black (the render already applies the citation/bibliography
  red). The source docx is not overwritten — the report's `output` field names a `<ad>_zref.docx`;
  **carry that path into the next step** (journalstyle formatting, peer review).
- If the report's `unknown_keys` is not empty, those markers stayed in the document on purpose: name them to
  the user and do not describe the section as finished.

## Report provenance (required)

The output/report presented to the user starts, right under the title, with this provenance block; it lists the
subagents **actually** called and the references **actually** read in that job (unused → `—`):

```
Skill: journalwriter
Subagent: <the ones called: journalwriter-s-danisman / journal-s-authorguidelines / journal-s-yayinstili / journal-s-notebooklm / journal-s-zotero>
References: <the ones read: journalwriter-s-danisman-r-bilgi.md>
NotebookLM: <the queried notebook name — queried for: Introduction / Discussion / —>
---
```

## Important rules
- Do not fabricate a citation — this skill's single red line. No non-real reference enters the text.
  `journalresearch` does the verification; trust its output, never produce a DOI/PMID from memory.
- Preserve the user's writing style and language; do not impose a generic tone.
- Place only the citation that **directly** supports the sentence; do not place a tangentially related article.
- This skill WRITES; the pure formatting/format job is `journalstyle`'s, **the citation/bibliography job is
  `journal-s-zotero`'s**. Write only the `{{zref:KEY}}` marker; never keep the bibliography by hand.

## Additional Resources

### Reference Files

- **`references/journalwriter-s-danisman-r-bilgi.md`** — distilled manuscript-writing knowledge; the source
  `journalwriter-s-danisman` derives its guidance from.
- **`references/journalwriter-s-danisman-r-guidelines/`** — reporting guidelines at item level:
  `ARRIVE.md` · `CARE.md` · `CONSORT.md` · `PRISMA.md` · `STARD.md` · `STROBE.md`, plus a `README.md`
  mapping study type → guideline. `journalwriter-s-danisman` reads the matching file; **`journalpeerreview` reuses this
  directory read-only** and must not modify it.
- Cross-skill contracts: the `{{zref:ITEMKEY}}` marker grammar lives in
  `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-zref-protocol.md`; NotebookLM knowledge
  in `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/notebooklm-r-rehber.md` (read by `journal-s-notebooklm`).

### Scripts

This skill ships none. It reuses `journalstyle`'s `journalstyle_workspace.py` and `journalstyle_extract_docx_structure.py`, called as
`${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/<name>.py`. It does **not** run the zotero
scripts itself — `journal-s-zotero` owns those (see the two-call contract in steps 5 and 6).
