---
name: writer
description: >-
  Bu skill, bir akademik makalenin bir bölümünü (Tartışma/Discussion, Giriş/Introduction,
  Sonuç, Özet/Abstract vb.) hedef derginin yazar kurallarına ve kullanıcının kaynak
  şablonuna uygun şekilde YAZMAK için kullanılmalıdır. Tetikleyiciler; "tartışma bölümünü yaz",
  "giriş yaz", "sonuç bölümünü yaz", "bu dergi için özet yaz", "makale metni oluştur",
  "şu bölümü [dergi adı] stiline göre yaz" gibi ifadeler. Kullanıcı bir makale bölümü
  YAZDIRMAK istediğinde bu skill kullanılır (yalnızca biçimlendirme/format istediğinde
  journalstyle kullanılır — o farklıdır). Bu skill metni yazarken, kanıt gerektiren
  ve kullanıcının atıf vermediği her bilimsel/klinik iddia için OTOMATİK olarak `research`
  skill'ini çağırıp gerçek, doğrulanabilir alıntılar (DOI/PMID) ekler.
---

# Writer — Section Writing + Automatic Citation

Starting from the user's thesis/data and the template they sent, you write a manuscript section
in the target journal's style. For every sentence in your text that needs evidence, you trigger the
`research` skill and propose a **real** citation. Never a fabricated citation.

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
  `PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/workspace.py" "<source.docx>" --slug <slug>`
  Use the `profiles_dir`, `yayinstili_slug_dir`, `authorguidelines_slug_dir` paths in the returned JSON.
- First look at `<profiles_dir>/<journal-slug>.json`.
- If not, call the **journalstyle-s-authorguidelines** subagent (in the same plugin) and create/cache the profile (under `<profiles_dir>`). The same rule as the journalstyle flow applies for the authorguidelines web+PDF checkpoint (the web summary is shown to the user).
- Use from the profile: `word_limit`, `section_order`, `abstract` rules,
  `citation_style` (Vancouver/APA/IEEE — pass this info to `zotero`; `zotero` applies the citation format/bibliography,
  you only write the `{{zref:KEY}}` marker), language and style hints.
- If a rule that cannot be verified is `null`, do not fabricate; warn the user.

### 3. Analyze the source and findings
- Examine the user's template/draft `.docx` with `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/extract_docx_structure.py`
  (current headings, tone, length, citation style). Match your writing style to it —
  imitate the user's voice, do not impose your own generic academic tone.
- For the Discussion/Conclusion, take the findings (tables, p-values, effect sizes) from the source.
  Write the **number/percentage/p-value format per the user's global rule**: in Turkish, a comma
  and `%` before the number (e.g. `%73,5`, `p=0,028`); in English, a period and `%` after
  (e.g. `73.5%`, `p=0.028`). Footnote statistical tests with the user's symbol standard.

### 3b. Get writing guidance — call `writer-s-danisman` automatically
**Before** writing the section, **call `writer-s-danisman` automatically with the Agent tool** (do not wait for approval),
in the same plugin. Give it this context: which section (Introduction/Methods/Results/Discussion/
Abstract/Conclusion), study type (RCT, cohort, case-control, cross-sectional, diagnostic, case report…),
PICO/hypothesis, and the current draft if any. From distilled manuscript-writing knowledge
(`references/writer-s-danisman-r-bilgi.md`), the subagent returns:
- that section's **IMRaD-based skeleton** (paragraph/subheading structure),
- what should be in each part (length, outcome order, Table 1/flow diagram, the ban on interpretation
  in Results, numeric presentation with 95% CI, the limitation paragraph in Discussion, etc.),
- the **reporting guideline** requests suited to the study type (STROBE/CONSORT/STARD/CARE/PRISMA),
- section-specific **common mistakes / checklist**.
Use this skeleton and criteria as the frame of your writing. Note: `writer-s-danisman` does **not produce
citations** — finding sources is `research`'s job in §5.

### 3c. Examine the publication/sample style — call `journalstyle-s-yayinstili` automatically
**Before** writing the section, **call the journalstyle-s-yayinstili agent automatically with the Agent tool**
(do not wait for approval), in the same plugin. Give it: target journal + slug + the source draft's
topic/keywords + **workspace paths** (`yayinstili_slug_dir`, `profiles_dir`) +
**(if the user gave a specific sample article — "write per this article", file/URL/DOI)**
`user_reference_article`. The agent produces/reads `<profiles_dir>/<slug>.yayinstili.json` (if a fresh
one exists, use it without regenerating). Use the returned **de-facto style** as the style frame of the §4
writing (together with §3b's advisor IMRaD skeleton):
- the dominant **tense/voice** (past/present, passive/active),
- **citation density** (how often in which section — tune the §5 research calls to this),
- the de-facto **section headings** and abstract structure,
- the **statistics presentation** (mean ± SD, 95% CI, p notation) — it does not conflict with the user's global
  number/p format rule, it is applied together with it.
Note: this agent only gives **observation**; it does not produce citations (that is §5 `research`'s job), you are the one who writes the text.
If the user did not give a sample article, the agent auto-selects similar samples from the journal.

### 3d. Literature material from NotebookLM (Introduction and Discussion)
The user's literature pool in NotebookLM is the raw-material source for two jobs: the **background/gap**
paragraphs of the Introduction and the **comparison with the literature** paragraphs of the Discussion.
Use the tools of the `notebooklm-mcp` MCP server
(`mcp__notebooklm-mcp__*`): `notebook_list`, `notebook_describe`, `notebook_query`,
`source_get_content`.

- **Find the notebook:** if the user gave its name, use it; if not, list with `notebook_list`
  and select the title matching the manuscript topic. If there are multiple candidates, ask the user.
- **Discussion — for each main finding**, ask the notebook with `notebook_query`: "Which studies support or
  contradict this finding (e.g. Y was higher in group X), and what did they find?" From the returned
  answers, extract: which study found what, the agreement/conflict direction with our finding,
  mechanism notes if any. These fill the skeleton of the "comparison with the literature (supporting/contradicting)"
  paragraphs in the §4 Discussion.
- **Introduction — for the topic/hypothesis**, ask the notebook with `notebook_query`: (a) "What is
  known about X — frequency/burden, the current standard approach?", (b) "Which questions remain
  unanswered, where do the studies disagree?", (c) "Which aspect of X has not been studied at all?"
  From the returned answers, extract: the background facts to be cited, the conflicting evidence, and
  the explicit knowledge gap. These fill the **problem → gap → aim** flow of §3b's advisor skeleton in
  the §4 Introduction.
- **Rule:** a NotebookLM answer provides background/discussion **content**, not a citation. Every study
  NotebookLM points to is verified via §5's `research` (with DOI/PMID); a `{{zref:KEY}}` is not written
  without verification. A reference coming from NotebookLM never turns directly into a citation.
- **Silent skip:** if the MCP server is not installed/connected, the session dropped (`nlm login`
  needed), or the section being written is **neither the Introduction nor the Discussion**, skip this
  step silently — the flow is not broken.
- Known limitation: NotebookLM has no official API; the server works over a browser session
  and may temporarily break when the Google side changes. If you get an error, suggest `nlm login` /
  `nlm doctor` to the user and skip the step.

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

### 5. Fetch citations automatically while writing — trigger the team member `research`
`research` is a team-member skill in the same plugin. When you write a paragraph and see that it contains a
claim needing evidence and the user did not give a citation for that sentence, **call the `research` skill
with the Skill tool** (do not wait for approval). That skill:
- looks first at the references the user gave, then the uploaded PDFs — while **always** scanning the user's fixed
  `pdflerim/` library (the PDF pool in the research skill's own folder) — then Consensus/PubMed,
- returns real, verifiable references with a DOI/PMID (does not fabricate),
- for each suggestion gives the evidence level + source + why-it-supports explanation.

**Actually use the article `research` found/suggested in the text — not just listing it:**
- **Use the source's finding to support/shape the sentence.** Do not just attach a dry marker to the end of a
  sentence and move on; touch what the article found into the text — e.g. "Su et al. similarly reported a
  decrease in delirium incidence {{zref:KEY}}" or "contrary to this, study X found no difference".
  This way, the evidence research brought contributes to the argument of the writing.
- **Place the citation as a marker — do NOT set its format yourself.** At the exact point where the sentence is
  supported, write the canonical `{{zref:ITEMKEY}}` marker (for multiple sources in the same sentence, grouped
  `{{zref:KEY1;KEY2}}`). The marker grammar is in one place: `../zotero/references/zref-protocol.md`.
  The in-text citation number/format (Vancouver `[1]`, APA
  author-year, etc.) and the bibliography list are **the `zotero` skill's authority alone** — do not embed a raw
  number or `(Author, Year)`, do not **keep** a bibliography list. This authority is in no other skill.
  - If the source is **in the Zotero library**: find the item key with `zotero_lib.py --search` and write
    `{{zref:KEY}}`.
  - If the source is **not in Zotero**: have it added to the library via the `zotero` skill's `add-methods`
    flow, get the key, then write the marker (if the user does not want to add it, leave the sentence without a
    marker and notify the user).
- `zotero` does the **duplicate** (same DOI/PMID) check during render; you use the same marker for the same source.
- If `research` says "no reliable evidence", do not fill the sentence with a **fabricated citation** — notify the user,
  suggest softening the sentence or providing a source.
- If the evidence is contradictory, reflect the uncertainty in the text (e.g. "the evidence is contradictory") and address both sides.

### 6. Present and report
- **Start the output with the provenance block** (see "Report provenance").
- Show the written section (with the citations as `{{zref:KEY}}` markers). In a separate part, list **each added
  citation's** research output format (Supported sentence · Reference · Why · Evidence level ·
  Source · Page/DOI/PMID) so the user can audit it.
- **Turning the citations into visible `[1]` and printing the bibliography is `zotero`'s job.** If the section will be
  written into a `.docx`: write the text with its markers, then call the `zotero` skill's `zotero_cite.py` refresh —
  the in-text citations and the bibliography list are created there. Do **not write the bibliography by hand.**
- Writing into a docx is subject to the global rule: **if an existing docx is updated, the added/changed text is red
  (RGB 255,0,0)**; a brand-new docx from scratch is black. Back up first. (`zotero_cite.py` already applies the
  citation/bibliography red.)

## Report provenance (required)

The output/report presented to the user starts, right under the title, with this provenance block; it lists the
subagents **actually** called and the references **actually** read in that job (unused → `—`):

```
Skill: writer
Subagent: <the ones called: writer-s-danisman / journalstyle-s-authorguidelines / journalstyle-s-yayinstili>
References: <the ones read: writer-s-danisman-r-bilgi.md>
NotebookLM: <the queried notebook name — queried for: Introduction / Discussion / —>
---
```

## Important rules
- Do not fabricate a citation — this skill's single red line. No non-real reference enters the text.
  `research` does the verification; trust its output, do not produce a DOI/PMID from your own memory.
- Preserve the user's writing style and language; do not impose a generic tone.
- Place only the citation that **directly** supports the sentence; do not place a tangentially related article.
- This skill WRITES; the pure formatting/format job is `journalstyle`'s, **the citation/bibliography job is
  `zotero`'s**. You write the `{{zref:KEY}}` marker; you never keep the bibliography by hand.
