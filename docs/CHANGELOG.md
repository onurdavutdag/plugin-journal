# plugin-journal — change history

Moved verbatim from `CLAUDE.md` on 2026-09-10 (entries were the `_Last update_` blocks of its
maintenance note, oldest first). New entries are appended here, not to CLAUDE.md.

> _Last update: 2026-07-25 — full `plugin-dev` spec audit (skill-development · agent-development ·
> plugin-structure): cross-boundary resource paths moved to `${CLAUDE_PLUGIN_ROOT}` (4 agents' knowledge
> paths did not resolve in a global install), all 5 agents given `model`/`color`/array `tools`/"When to
> invoke"/"Edge Cases", all 5 SKILL.md bodies rewritten in imperative form, zotero references renamed to
> `zotero-r-*`, manifest description/metadata corrected; version 1.4.0._
>
> _Last update: 2026-07-25 — rename: the marketplace (`onur-plugins`), the local source folder
> (`journal-plugin`) and the GitHub repository all became **`plugin-journal`**; install id is now
> `journal@plugin-journal`. No component was added or removed; version 1.4.1._
>
> _Last update: 2026-07-25 — validation pass: the licence contradiction resolved (`plugin.json` no longer
> claims MIT; the personal-use `skills/journalresearch/LICENSE.txt` moved to a plugin-wide root `LICENSE.txt`),
> `allowed-tools` removed from `peerreview/SKILL.md` so all 5 skills are unrestricted and consistent
> (journalstyle/writer/research need Task + MCP tools, so a restricted list would break them), and the
> section-10 inventory completed with the three previously missing files; version 1.4.2._
>
> _Last update: 2026-07-25 — the plugin gained its first **command**: `commands/journal.md` (`/journal`),
> a single entry point that reads the user's request, picks the owning skill/agent and hands the job
> over; with no argument it asks with `AskUserQuestion`. It was made a command rather than a sixth
> (router) skill so that it fires only when typed and does not compete with the 5 skills' own
> natural-language triggers; version 1.5.0. **1.5.1:** `argument-hint` quoted — an unquoted value
> starting with `[` is parsed by YAML as a flow sequence (a list), not the string the loader expects._
>
> _Last update: 2026-07-25 — **script hardening round** (external audit, verified claim by claim).
> `zotero_cite.py`: the source docx is no longer the default output (`<ad>_zref.docx`; an explicit
> `--out` onto the source takes a `.bak`), paragraphs are rewritten run-surgically so italics/bold/
> super-subscript/hyperlinks **and existing `ZOTERO_*` fields** survive, text is read through
> `.//w:r` (hyperlink runs included), old-bibliography deletion is bounded to WJ-tagged paragraphs,
> `unlink --mode field` prints ONE json and saves nothing, markers match case-insensitively.
> `apply_profile.py`: partial `margins_cm`, numeric `line_spacing`, table/header/footer paragraphs,
> warnings for anything not applied; dead `CM_TO_TWIPS` removed. `extract_docx_structure.py`: anchored
> ("wrap text") figures counted. `workspace.py`: warns when the target file does not exist; one shared
> case-insensitive PDF listing reused by `extract_pdf_text.py`, whose `--full` is now capped.
> `pubmed_eutils.py`: `NCBI_EMAIL`/`NCBI_API_KEY` from the environment (the fake `example.invalid`
> address is gone). `zotero_lib.py`: consistent snapshot via `sqlite3.Connection.backup()` + a
> per-PID temp name. New shared helper `skills/journalstyle/scripts/docx_util.py`. All 5 SKILL.md
> `version:` fields aligned with the manifest; version 1.5.2._
>
> _Last update: 2026-07-25 — the plugin gained its **6th agent**, `zotero-s-teacher`, and the `zotero`
> skill became **two-mode**. Distilled from six Zotero video transcripts (Aklan & Salih · Türkel &
> Ateş · Grad Coach · Gömek · Koç ders 11 · Koç & Tekno Akademi) and gap-filled against the NotebookLM
> `zotero` notebook, six Turkish teaching references were added under `skills/zotero/references/`
> (`zotero-r-{kaynak-ekleme,atif-stilleri,eklenti-senkron,ilahiyat,organizasyon,tuzaklar}.md`). The
> agent teaches the GUI workflow only — no `Write`/`Edit`/`Bash`, so docx citation work stays the
> skill's own operational flow (§7 unbroken). It must state the Zotero version behind every step,
> refuse certainty on the ⚠️ items the videos left unclear, and make the user take a backup before
> any data-losing operation. It merged into the existing `zotero` skill rather than becoming a
> separate skill so the two would not compete on the word "zotero"; version 1.6.0._
>
> _Last update: 2026-07-25 — **`control-codebase` audit** (`kod-denetim-raporu 20260725 2207.md`):
> 0 critical, 9 medium, 5 low, all 14 fixed. The 1.6.0 change had left three routing surfaces
> behind (root `README.md` still said "5 agents", `commands/journal.md` and §3 above did not know
> the teaching mode) — fixed, and the maintenance rule now names all four surfaces so the omission
> cannot repeat. Four agents' `description` was **not valid YAML** (an unquoted scalar containing
> `: ` — the same bug class as the 1.5.1 `argument-hint` fix); all now single-quoted, and
> 12/12 frontmatter blocks parse under strict PyYAML. Script fixes: `docx_util.py` gained
> `iter_runs()` (hyperlink runs, which `Paragraph.runs` cannot see) and `to_float()` (Turkish
> decimal comma) — `apply_profile.py` uses both; `extract_pdf_text.py` survives a corrupt PDF;
> `zotero_lib.py` matches short PMIDs and really filters by collection key; `zotero_cite.py` no
> longer inserts a blank paragraph at the top in field mode, no longer writes `[?]` for an unknown
> key, and walks the document in true document order so Vancouver numbering follows first
> appearance; `pubmed_eutils.py` no longer signs third-party queries with the author's address.
> Version 1.6.1._
>
> _Last update: 2026-07-25 — **the `zotero` skill was removed; zotero is now two plugin-level agents.**
> `journal-s-zotero` (operation: sqlite/local-API access + the docx citation/bibliography) and
> `journal-s-zotero-teacher` (renamed from `zotero-s-teacher`). Reason: nothing ever called zotero *as
> a skill* — writer and research ran its scripts directly, so the skill was a wrapper around two
> scripts, 11 references and the single-ownership rule. As an agent the library dump (hundreds of
> records) stays out of the caller's context. The two could not merge into one agent (9,354 + 9,922
> chars against a 10,000 limit), so they stay peers sharing one reference pool. `references/zotero-r-*`
> (11 files + the new `zotero-r-word-flow.md`) and `scripts/zotero_{cite,lib}.py` moved to the **plugin
> root** — the `journal-s-notebooklm` precedent for a component no skill owns. writer now uses a
> **two-call contract**: source list → `{source → ITEMKEY}` map, then docx path → render report.
> No script logic changed. §4.4 deleted, peerreview renumbered 4.4; version 1.7.0._
>
> _Last update: 2026-07-26 — **`klasoredit:klasoreditplugin` naming rule applied retroactively**
> (`plugin-ad-denetle.py`: 3 N4 errors + 7 N6 warnings). Skill names now carry the plugin prefix:
> `writer` → **`journalwriter`**, `research` → **`journalresearch`**, `peerreview` →
> **`journalpeerreview`** (`journalstyle` already conformed); their reference files moved with them
> (`journalresearch-r-*`, `journalpeerreview-r-common-issues.md`, `journalwriter-s-danisman-r-*`).
> Every agent gained a `skills:` array declaring its owner — and once
> `journalstyle-s-authorguidelines` / `journalstyle-s-yayinstili` declared **two** callers
> (journalstyle + journalwriter), the rule ("more than one skill → plugin prefix") renamed them to
> **`journal-s-authorguidelines`** / **`journal-s-yayinstili`**. Housekeeping: `.claude/*.local.md`
> added to `.gitignore` (S6), the plugin-root `output/` folder and the old audit report moved out of
> the tree (S8 — a `.gitignore` entry does not stop `marketplace update` from copying them). The
> maintenance-log entries **above this line keep the pre-1.8.0 names on purpose** — they are history,
> not current state. Version 1.8.0._
>
> _Last update: 2026-07-27 — **`journal-s-zotero-teacher` removed; the plugin is down to 6 agents.**
> The user knows the Zotero GUI and does not need a teacher, so the agent and its six Turkish
> teaching references (`zotero-r-{kaynak-ekleme,atif-stilleri,eklenti-senkron,ilahiyat,organizasyon,
> tuzaklar}.md`, distilled from six video transcripts) were deleted. Safe because the two reference
> pools never overlapped: the operation agent reads only `zotero-r-{word-flow,zref-protocol,
> citation-format,add-methods,styles,storage-bridge}.md`, and its own §2 forbade loading the teaching
> files — so the `journalwriter → journal-s-zotero → journalstyle` citation flow is untouched. The
> agent had `skills: []` and no skill ever called it (user + `/journal` only), so nothing lost a
> callee. Knock-on fixes: directly callable agents are now **two** (notebooklm, zotero), the
> "7 agents / 6 colours" collision paragraph is gone, and `journal-s-notebooklm` is at last the
> **only** component reaching the NotebookLM MCP (the teacher was its single exception). A Zotero
> how-to question now has no owner — `/journal` says so and stops instead of pointing at a component
> that does not exist. The deleted content stays recoverable from git history. Version 1.9.0._
>
> _Last update: 2026-07-27 — **`plugin-dev` spec audit of the two profile agents' skill contracts.**
> Three findings, all fixed. (1) **Least privilege:** `journal-s-authorguidelines` declared `Write`
> but its own body forbade writing the final `<slug>.json` — `Write` removed from `tools`. Its
> sibling `journal-s-yayinstili` keeps `Write` because it genuinely uses it. (2) **Undefined output
> contract:** `journal-s-yayinstili` had no `## Output Format` section — the spec's DON'T list names
> exactly this ("leave output format undefined") — while `journalwriter` §3c consumed "the returned
> style". Added, and the Method's field enumeration (a verbatim restatement of the schema the agent
> already `Read`s) moved to the reference as "What to measure": body 9,738 → 8,681 chars, back under
> the 10,000 limit with room to spare. Method numbering 1·2·2b·**4**·5·6 corrected. (3) **Contradictory
> freshness contract — the behavioral fix:** `journalstyle` 2.5 put the `<slug>.yayinstili.json`
> freshness check in the skill, `journalwriter` §3c delegated it to the agent, and **the agent
> implemented neither** — so writing each section paid a full agent run plus PDF extraction even with
> a warm cache. Both callers now check the cache first and skip the agent entirely when it is fresh.
> Housekeeping against skill-development's anti-duplication rule: the two call procedures now live
> once each in `journalstyle-r-{authorguidelines,yayinstili}.md` ("Call procedure"), and all four
> SKILL.md call sites point there. Version 1.10.0._
>
> _Last update: 2026-07-27 — **dead-reference sweep after the 1.7.0 and 1.9.0 removals.** No behaviour
> was redesigned; six files still named components that no longer exist. `zotero` stopped being a
> **skill** at 1.7.0 (it became the `journal-s-zotero` agent) but was still called one in
> `journalresearch/SKILL.md` — **including its frontmatter `description`**, the text Claude reads when
> routing — in `journalwriter/README.md` (where the call table even typed it `skill`), in
> `references/zotero-r-{zref-protocol,citation-format}.md` (`OWNER: zotero`) and in the root
> `README.md`. The one **runtime** instance: `apply_profile.py` printed *"`zotero` skill'i ile
> uygulanmalı"* to the user at line 135 — it now names the agent. Second class of rot: the `zotero-r-`
> prefix rename left **7 internal pointers** on the pre-rename filenames (`citation-format.md`,
> `add-methods.md`) inside `zotero-r-zref-protocol.md` and `zotero-r-styles.md` — a `Read` on those
> names fails, so the marker protocol could not reach its own format definition. Also fixed:
> `marketplace.json` still advertised "Zotero rehberliği / öğretimi" although the teacher agent went
> at 1.9.0 (`plugin.json` had been updated, the marketplace half of the pair was missed — and it is
> the text shown at install); `commands/journal.md` said "two of the **seven** owners are agents"
> when the §2 table's seventh row points *outside* the plugin, so six is the count; and §5's agent
> table had a stray blank line that split the `journal-s-zotero` row into a separate headerless
> table. The 4 SKILL.md `version:` fields were re-aligned to the manifest (1.8.0 → 1.10.0) — note
> that the sync hook's automatic patch bump reopens a one-patch gap after every commit, so this
> alignment is a manual, recurring act, not a steady state. The changelog entries above keep their
> historical names on purpose._
>
> _Last update: 2026-07-27 — **`plugin-dev` spec audit of the journalwriter team** (the five agents
> journalwriter calls + its own SKILL.md). The 1.10.0 audit had fixed the two *profile* agents; the
> same defect classes were still present in the other three. (1) **Undefined output contract —
> `journalwriter-s-danisman`:** the only one of the five with no output section at all, the spec's
> named DON'T. `journalwriter` §3b had been compensating by restating the four return items. The agent
> now declares `## Output Format` (Skeleton · Content rules · Reporting guideline items · Common
> mistakes, plus a Critique block when a draft was passed, plus the `guideline_items: not in package`
> signal), its Method stopped re-enumerating them, and §3b shrank to a pointer. (2) **Least privilege
> — `journal-s-notebooklm`:** `tools` carried `Write`, `Bash`, `Grep`, `Glob` and the body called
> **none** of them — the artifact tools write their own files, and running `nlm login` is explicitly
> forbidden at line 103, which was the only Bash candidate. Now `["Read", …26 MCP tools]`; §5's tool
> column updated with it. (3) **Anti-duplication:** the NotebookLM call procedure lived in three places
> at once — `journalwriter` §3d (27 lines), `journalresearch` Step 1b (17 lines) and the agent's own
> body. It now lives once, as `notebooklm-r-rehber.md` **§11 "Call procedure"** (same shape and same
> end-of-file position as the two `journalstyle-r-*` precedents), carrying when-to-call, the brief,
> what-comes-back and the two binding rules (content-never-a-citation · silent skip); both callers
> point there. Housekeeping: provenance blocks added to `journalwriter-s-danisman`,
> `journal-s-authorguidelines` and `journal-s-notebooklm`, so all six agents now open a report the same
> way — `journalwriter`'s own provenance block asks which references the subagent read, and until now
> three of them never said. `journal-s-zotero` lost a dead `<!-- Oluşturma -->` comment and an `# Rol:`
> H1 that no sibling carries, and its `## Adım 1/2/3` headings became English like every other agent's.
> `## Return format` / `## Output format` normalised to the spec's `## Output Format`. No behaviour was
> redesigned; §3d, Step 1b and §3b are the same flows, described once instead of twice._
>
> _Last update: 2026-07-27 — **the version ratchet is closed; `SKILL.md` no longer carries a
> `version:` field.** Two turns in a row the four fields were hand-aligned to the manifest and were
> stale again within minutes: the sync hook bumps the patch on `Stop`, i.e. **after** the commit, so
> a hand-kept copy is structurally always one behind. Investigation settled it — **no script and no
> validator reads the field** (the validator's S2 compares `plugin.json` against
> `installed_plugins.json` only), the spec requires just `name` + `description`, and the two sibling
> plugins had already proven the field inert: `plugin-uygulama` sat at manifest 4.1.2 with skills on
> 1.0.0/1.0.1/2.4.0, `plugin-klasoredit` at 1.6.12 with skills on 1.0.0, for months, with nothing
> breaking. Removed from all **11** SKILL.md files across the three plugins; `plugin.json` is now the
> single place a version is written. The other half of the fix is in the hook itself
> (`~/.claude/hooks/sync-yerel-global*.js`): it wrote `plugin.json` but left the repo dirty, so every
> session ended with an uncommitted manifest — the rule text even admitted it ("commit + push hâlâ
> elle"). `syncPlugin` now calls `commitVersionBump` **after** the install verifies, committing that
> one file **pathspec-limited** (`git commit -- .claude-plugin/plugin.json`, never `git add -A`) and
> pushing without `--force`; a non-git folder or a missing `origin` is skipped silently, a failed
> install is deliberately **not** committed so the dirty bump stays visible as the failure signal, and
> every git error goes to `notes` without breaking the turn. Content commits stay manual on purpose —
> they need a real message and a review. Rule text updated at its single source,
> `klasoredit:klasoreditplugin` → `references/senkron-kurali.md`._
>
> _Last update: 2026-07-27 — **the publisher PDFs left the plugin tree.** An audit found the 10 sample
> article / author-guideline PDFs still sitting under `skills/journalstyle/references/{yayinstili-pdf,
> authorguidelines-pdf}/` — the location §4.1 had already marked as superseded by the workspace model.
> `.gitignore` `*.pdf` kept them out of git (S5 clean, nothing ever pushed), but **`marketplace update` +
> `install` copy the whole tree**, so every one of the 21 installed version folders under
> `~/.claude/plugins/cache/plugin-journal/journal/` carried its own set: **210 copies, 140 MB — 87 % of the
> entire plugin cache.** The folders were moved to `Desktop\claude working\output\journal-pdf-arsiv\`
> (files kept, nothing deleted) and the stale cache versions purged. `.gitignore` keeps `*.pdf` as a second
> line of defence. Two documentation contradictions went with it: the README credited `journalstyle` with
> "citation format" (§7 gives docx citation/bibliography to `journal-s-zotero` alone) and listed only four
> of journalwriter's six sections. The rule side was patched at its source — `klasoredit:klasoreditplugin`'s
> validator now flags a `.pdf` anywhere in a plugin tree under **S8** (the rule text already claimed S8
> covered this; only the script did not) and no longer misreads a deliberate `skills: []` as a missing
> field, which had produced a false N6 warning on `journal-s-zotero` every run._
>
> _Last update: 2026-07-28 — **`journal-s-zotero` audited against `plugin-dev` (agent-development ·
> skill-development · mcp-integration); an unexecutable instruction chain was found and closed.**
> `references/zotero-r-add-methods.md` told the agent to call three `mcp__claude_ai_PubMed__*` tools
> plus `WebFetch` and `WebSearch`, while the agent's `tools` array is
> `["Read", "Glob", "Grep", "Bash"]` — and `tools`, once given, **restricts**. Four of the five add
> methods could not run as written, and body Rule 2 named "PubMed MCP / the journalresearch skill",
> neither of which the agent can reach (it holds no `Skill`/`Task` tool either). Fixed **without
> widening the tool array**: verification now runs on `skills/journalresearch/scripts/pubmed_eutils.py`
> through Bash — NCBI E-utilities needs no authentication, so the path also survives a
> non-interactive session. What that path genuinely cannot resolve (ISBN, arXiv, a DOI absent from
> PubMed) is now declared out of scope instead of being silently attempted. Widening the array was
> rejected on purpose: source finding/verification is **journalresearch's** authority under §7, and a
> PubMed MCP dependency fails silently wherever the connector is unauthorized._
>
> _Same pass: the library **write** left the reference as a raw HTTP block while `zotero_lib.py` is
> deliberately read-only, so the agent hand-rolled `curl` every time. It now has its own script,
> **`scripts/zotero_save.py`** — de-duplication on DOI/PMID before any POST, `zotero_closed` returned
> with the prepared payload instead of a failed write, one JSON object per run
> (`status`/`itemkey`/`duplicate_of`/`prepared`), `--dry-run`, and `zotero_lib.py` untouched so its
> read-only guarantee still holds. Verified against the real library: `duplicate` correctly returned
> the existing key for a DOI already present, and a live (non-dry-run) call with Zotero closed wrote
> nothing. The body also gained the two sections `plugin-dev`'s template requires — **Your Core
> Responsibilities** and a numbered **Process** — and the root `README.md` finally documents
> `ZOTERO_DATA_DIR` and the rest of the prerequisites, which mcp-integration requires of any plugin
> depending on environment variables._
>
> _Last update: 2026-07-28 — **`journalresearch` and every contract around it audited against the same
> three `plugin-dev` skills.** The skill itself came out clean: third-person description with trigger
> phrases, 1327-word imperative body (`you`/`your`: **zero**), no meaningful duplication with its three
> references. The defects were all in the seams. **The binding output template could not record tier 3:**
> `journalresearch-r-kunye.md` allowed `Source` values `<User-provided reference | Uploaded PDF |
> Consensus>` — no NotebookLM — and hardcoded `Subagent: —`, so obeying the template (which SKILL.md
> calls "the exact template") erased the `journal-s-notebooklm` call from the provenance block the whole
> auditability claim rests on. Both fixed, plus a worked tier-3 example._
>
> _Two authority leaks closed. `journalresearch-r-pdf.md` had journalwriter "add it to the reference
> list, de-duplicating by DOI/PMID" — §7 gives the docx bibliography to `journal-s-zotero` alone — and
> had journalresearch run `zotero_lib.py` itself, an invisible dependency that appeared nowhere on the
> component map. The rule is now stated once and shared with `zotero-r-storage-bridge.md`: **querying
> the library is the agent's, reading a PDF already on disk is the skill's.** `journal-s-zotero` gained
> a fifth job for it (return items + attachment paths, do not open the PDFs). The undocumented
> `mcp__claude_ai_Google_Drive__*` path was removed rather than declared — PDF discovery is now
> `pdflerim/` + workspace + a Zotero collection through the agent._
>
> _Contract drift swept: CLAUDE.md §4.3 listed three source tiers where the skill defines four (tier 1,
> the user's own references, was missing); journalwriter §5 described journalresearch's tiers without
> NotebookLM although §3d calls that agent itself, and never mentioned carrying the provenance block
> through; the same call was named "Agent tool" in two files and "Task" in two others — now uniformly
> **`Task`**. `journal-s-notebooklm` contradicted itself on notebook choice ("You pick the notebook" vs
> "ask the user — never guess") and shipped query shapes for only one of its two callers; it now has a
> third shape, *claim verification*, for the journalresearch tier. Its bold pseudo-headings were left
> alone — that is `agent-development`'s own Standard template, not a deviation._
>
> _Last update: 2026-07-28 — **the rest of the plugin audited against the same three `plugin-dev`
> skills** (the surface the previous three passes had not reached: `journalwriter` · `journalstyle` ·
> `journalpeerreview` and the four agents `journal-s-authorguidelines`, `journal-s-yayinstili`,
> `journalstyle-s-docxformat`, `journalwriter-s-danisman`, plus the command, the scripts and both
> manifests). The base held: 4/4 skills third-person + imperative (1092–2011 words), 6/6 agents with
> complete frontmatter and "When to invoke"/"Edge Cases", 10/10 scripts compiling with CLI signatures
> matching their call sites, and no instruction naming a tool its `tools` array forbids. **The one real
> defect was a promise with no implementation:** `journalstyle` §3 and `journalstyle-s-docxformat` step 5
> both offered to add a missing required section automatically, but `apply_profile.py` only *warned*
> about `required_sections`, the agent's only docx-capable tools were `Write`/`Edit` (a `.docx` is a zip
> — writing it as text corrupts the file), and the agent's own example told it to put **markdown**
> `## Data Availability Statement` into Word. Per the user's decision the promise was kept and made real:
> `apply_profile.py` moved to argparse and gained **`--add-sections`**, appending each missing section to
> the end of the file as a genuine Word `Heading 1` + `[Bu bölüm doldurulacak]` placeholder, falling back
> to a bold plain paragraph (with a warning) when the template has no `Heading 1` style, and leaving
> section **order** untouched. A flagless call behaves exactly as before, so the existing three-argument
> call sites keep working. Style availability is probed **once, before any insert** — `add_paragraph(text,
> style=…)` inserts first and assigns the style after, so a missing style used to leave an orphan
> paragraph behind. Knock-on: the agent's `tools` dropped to `["Bash", "Read"]` (the 1.10.0 and 1.11.0
> least-privilege precedent), and it finally got the **provenance block** the other five have — the
> 1.11.0 entry's "all six agents now open a report the same way" was true of five until today._
>
> _Same pass, housekeeping: **9 cross-component pointers were bare relative paths.** The worst sat in
> `journalresearch-r-pdf.md` — a skill that **has** its own `references/` folder pointing at the
> plugin-root pool, so `references/zotero-r-zref-protocol.md` resolved to a real but wrong directory
> rather than failing loudly; the other eight are the zotero pool's sibling pointers and two in
> `journal-s-zotero`. All now carry `${CLAUDE_PLUGIN_ROOT}`, as §2 has required since 1.4.0. §2's "12
> reference files" is **7** since the 1.9.0 teacher removal (6 `zotero-r-*` + `notebooklm-r-rehber.md`),
> and the last second-person sentence in any SKILL.md body (`journalwriter` §5) is gone — all four are at
> zero. Version 1.14.0._
>
> _Last update: 2026-07-28 — **every script now carries its owner in its name.** Plugin, skill, agent and
> command names have followed N1-N11 since 1.8.0 and reference files follow `<owner>-r-<topic>.md`, but
> scripts had **no rule at all**: `workspace.py`, `apply_profile.py`, `pubmed_eutils.py` said nothing
> about whose they were. Seven files were renamed to `<owner>_<role>.py` — five under
> `skills/journalstyle/scripts/`, two under `skills/journalresearch/scripts/`. The three plugin-root
> `zotero_{cite,lib,save}.py` were already `<topic>_<role>` and stayed. **The separator is an underscore,
> not a hyphen**, and that is not a style choice: three of these files import each other as Python
> modules (`from journalstyle_docx_util import …`, `from journalstyle_workspace import …`) and a module
> name cannot contain a hyphen — so N9's kebab-case rule does not reach scripts. Cost as measured:
> 7 renames, 3 import lines and **111 filename occurrences across 25 files**, plus the component map's
> three script nodes. The maintenance entries above keep the pre-rename names on purpose, the same
> convention the 1.8.0 rename entry set — they are history, not current state._
>
> _Same pass: the rule was written down at its source rather than left as a habit.
> `klasoredit:klasoreditplugin` gained **N12** in `references/adlandirma-kurali.md` and a matching check
> in `scripts/plugin-ad-denetle.py`, so the pattern is now machine-verified on every audit. Severity is
> **UYARI**, because the rule is not retroactive — it binds scripts created or edited from now on, the
> same precedent the README rule set. The validator's own `plugin-ad-denetle.py` is therefore the one
> file that fails N12 (it carries hyphens); it was deliberately left alone. Version 1.15.0._
>
> _Last update: 2026-07-28 — **`page_size` was never applied.** Found while walking the script's
> execution for the user: in `journalstyle_apply_profile.py` the `if page_size == "A4"` block sat
> **inside `for key in bad:`** — the loop that reports margin values which could not be parsed. So the
> page size was applied only when a `margins_cm` entry was malformed, and even then it wrote to the
> leaked `section` variable from the earlier loop, i.e. the **last** section only. With a normal profile
> nothing happened at all, while the journalstyle flow kept reporting "A4 applied" — a silently false
> compliance report on a submission-critical field. The size lookup now resolves once (`{"A4": …,
> "Letter": …}`), an unrecognised value warns once instead of per bad margin, and the assignment moved
> into the `for section in doc.sections` loop so **every** section gets it. Verified on four profiles
> (A4 · Letter with a Turkish `"2,5"` margin · unrecognised `B5` · no `page_size` at all) and on a
> three-section document — all three sections became A4, where the old code would have changed one.
> Version 1.15.1._
>
> _Last update: 2026-07-29 — **`journalstyle_workspace.py` → `journalstyle_calismaklasoru.py`.** The
> user needed three turns to work out what "workspace" named, so the Step 0 script now says its job in
> the user's own language: it resolves the **çalışma klasörü** — the folder holding the source `.docx`.
> The Turkish-lettered form the user first proposed (`calısmaklasoru`) was **refused**: this file is
> imported as a Python module (`from journalstyle_calismaklasoru import pdf_paths`), `ı` (U+0131) is
> indistinguishable from `i` at a glance so a mistyped import fails at runtime, and
> `klasoredit:klasoreditplugin` **N9** bans `ö/ü/ş/ğ/ç/ı` outright. The name is therefore pure ASCII and
> still satisfies **N12** (`<owner>_<role>.py`); the separator stays an underscore because a module name
> cannot carry a hyphen. Cost as measured: **22 occurrences across 9 files**, of which exactly **one was
> executable** — the import at `journalstyle_extract_pdf_text.py:27`; the other 21 were call lines and
> prose. Nothing else changed: no flag, no JSON key, no behaviour. The four routing surfaces needed only
> one — the root `README.md`, `commands/journal.md` and `plugin.json` never named the script. Sibling
> scripts keep their English roles, so `journalstyle/scripts/` is now mixed-language on purpose; the rule
> binds the name's **shape** (`<owner>_<role>`, ASCII), not its language. The manifest also moves to
> **1.16.0**, the number §2 and the script's own `LEGACY_SUBDIRS` comment had already been claiming for
> the workspace-layout change while the manifest sat at 1.15.x. The changelog entries above keep the
> pre-rename name on purpose — the same convention the 1.8.0 and 1.15.0 rename entries set._
>
> _Last update: 2026-07-29 — **`zotero_lib.py` → `zotero_kutuphaneoku.py`.** Second rename of the
> same day, same reasoning as `calismaklasoru`: `lib` named the file's *shape*, not its job, and it
> named it wrongly. "Library" reads as a generic helper module — but the shared helper in this repo
> is `journalstyle_docx_util.py`, and this file's defining property is that it **only reads**: writes
> were deliberately split into `zotero_save.py` precisely so the read-only guarantee stays auditable.
> The new name says the job in the user's own language: it reads (`oku`) the Zotero library
> (`kutuphane`). Pure ASCII, for the same reason as last time — `zotero_save.py` imports it as a
> Python module, and **N9** bans `ö/ü/ş/ğ/ç/ı`; `<konu>_<rol>` keeps **N12** satisfied with `zotero`
> as the topic (a plugin-level script is owned by no skill). Cost as measured: **37 occurrences
> across 11 files**, of which **8 were executable** — `zotero_save.py`'s `import` plus its five
> attribute uses (`LOCAL_API`, `api_alive`, `_open_copy`, `_load_all`, `_extract_pmid`), and
> `zotero_cite.py`'s two `os.path.join(..., "zotero_lib.py")` subprocess paths. An import alias was
> refused: `import zotero_kutuphaneoku as zotero_lib` would keep the discarded name alive in code.
> Two strings that embedded the old file name followed it — the temp-copy prefix
> (`zotero_kutuphaneoku_copy_<pid>`) and `zotero_cite.py`'s JSON error key
> (`zotero_lib_failed` → `zotero_kutuphaneoku_failed`, consumed by no `.md` and by no external
> caller). No flag, no CLI surface and no behaviour changed. The five remaining `zotero_lib.py`
> mentions all sit in changelog entries above and keep the pre-rename name, per the standing
> convention._
>
> _Last update: 2026-07-29 — **the zotero trio finished: `zotero_save.py` → `zotero_kutuphaneyaz.py`,
> `zotero_cite.py` → `zotero_docxatifbas.py`.** The three plugin-root scripts now state their one
> authority each in the same language and the same shape: `zotero_kutuphaneoku` reads the library,
> `zotero_kutuphaneyaz` writes to it, `zotero_docxatifbas` renders citations into the docx. The user
> proposed `zotero_docxatıfbas.py`; the dotless `ı` was **refused** for the third time on the same
> grounds — **N9** bans `ö/ü/ş/ğ/ç/ı` in file names outright, U+0131 is indistinguishable from `i` at
> a glance, and the plugin spec allows no non-ASCII in name fields. Only the letter changed, the
> intent did not. Cost as measured: **53 occurrences across 14 files**, of which **zero were
> executable** — unlike the `zotero_lib` rename, nothing imports these two and nothing builds their
> filename as a subprocess path (`zotero_docxatifbas.py` calls `zotero_kutuphaneoku.py`, never the
> reverse). The nearest thing to a live surface was `journalstyle_apply_profile.py:201`, a warning
> string **printed to the user**, and the ready-made Bash call blocks in `agents/journal-s-zotero.md`
> that the agent runs verbatim. No flag, no JSON key, no CLI surface and no behaviour changed. The
> eight remaining old-name mentions all sit in changelog entries above, per the standing convention._
>
> _Last update: 2026-07-29 — **the naming pattern reached the skill scripts: five renames in one
> pass.** `journalstyle_apply_profile` → **`journalstyle_docxbicimuygula`**,
> `journalstyle_extract_docx_structure` → **`journalstyle_docxyapicikar`**,
> `journalstyle_extract_pdf_text` → **`journalstyle_pdfmetincikar`**,
> `journalresearch_search_pdfs` → **`journalresearch_pdfara`**, `journalresearch_pubmed_eutils` →
> **`journalresearch_pubmedara`**. The rule the four preceding renames had settled into, stated once:
> the owner prefix is fixed by **N12**, the role names the file's **job** (not its shape) as
> `<object><verb>` in Turkish, pure ASCII per **N9**, and it must separate the file from its
> siblings. So `docxbicimuygula` writes the docx and `docxyapicikar` reads it — a pair the English
> names hid; `pubmed_eutils` named an API where `pubmedara` names the work.
> **`journalstyle_docx_util.py` was deliberately left alone**: the reason `lib` was rejected does not
> apply to it. That file *is* a library — no CLI, only `iter_paragraphs`/`count_drawings`/
> `utf8_stdout`, imported by its siblings — so "util" states its job correctly. Cost as measured:
> **81 occurrences across 25 files**, of which **zero were executable**: the only script-level
> imports in the repo target `journalstyle_docx_util` and `journalstyle_calismaklasoru`, and neither
> was renamed. The live surfaces were prose call lines — three agents' ready-made Bash blocks, four
> SKILL.md flows, and `journalstyle_docxyapicikar.py:63`, a usage string **printed to the user**
> (the same class as `apply_profile.py:201` in the entry above). No flag, no CLI surface, no
> behaviour changed. Three old-name mentions remain, all in changelog entries, per convention._
>
> _Last update: 2026-07-29 — **`journalstyle_docx_util.py` → `journalstyle_docxgorunmeyenigorur.py`.**
> The entry above says this file was deliberately left alone; the user later decided otherwise, and
> that decision stands. The name states what the file does: it sees what `python-docx` cannot —
> paragraphs inside table cells, headers and footers (`Document.paragraphs` misses them), runs inside
> a `<w:hyperlink>` (`Paragraph.runs` misses them), anchored "wrap text" images (`inline_shapes`
> misses them). The proposed `journalstyle_docxgörünmeyenigörür.py` was **refused** on `ö`/`ü` — this
> file is imported as a Python module, so **N9** applies with teeth here, not merely as convention.
> **The trade-off was stated before the rename and the user chose anyway:** two of the seven functions
> have nothing to do with docx (`to_float` parses the Turkish decimal comma, `utf8_stdout` fixes the
> Windows console), so the name over-claims by about a third. Recorded here rather than argued again.
> **This was the first rename in the series with genuinely executable references** — the nine before it
> had zero. Two `import` lines, in `journalstyle_docxbicimuygula.py:26` and
> `journalstyle_docxyapicikar.py:16`; either one left stale kills the script with
> `ModuleNotFoundError`. They were changed in the same pass as the `git mv`, with no aliasing, and both
> scripts were run immediately afterwards to prove the chain. Cost: **14 occurrences across 6 files, in
> two plugins** — `plugin-klasoredit` had to move too, because `klasoreditplugin-s-scriptadlandirma`
> cites this very file as the precedent for its genuine-library exception. That rule was rewritten from
> "a library keeps its shape-name" to "a shape-name is not a defect, but the owner may prefer a
> job-name" — the evidence test (does it have a CLI?) is unchanged._
>
> _Last update: 2026-07-30 — **both halves of the journalwriter ↔ `journal-s-zotero` contract were
> section-scoped; both are now manuscript-scoped.** The question that opened this was whether
> `journal-s-zotero` should be *owned* by journalwriter (`skills: ["journalwriter"]`). It should not, and
> the reason is worth recording so it is not re-asked: **`skills:` is not a runtime field** — the
> `plugin-dev:agent-development` frontmatter schema is `name` · `description` · `model` · `color` ·
> `tools`, dispatch happens through `Task` + `subagent_type`, and no array gates it. The field exists for
> `klasoredit`'s N6 validator alone. So ownership buys **zero** efficiency, while N6 would then force the
> rename `journal-s-zotero` → `journalwriter-s-zotero` (**104 occurrences across 28 files**) and make a
> false claim: the agent has five callers (journalwriter · journalstyle · journalpeerreview ·
> journalresearch · `/journal`), which is exactly why 1.7.0 gave it `skills: []` and 1.9.0 left it
> directly callable. The `skills: []` stays._
>
> _What was actually costing something sat in `journalwriter` §5 and §6, both of which said "per
> section". **§5, key resolution:** the map is now held for the whole manuscript and later sections send
> only a **delta**; an empty delta calls the agent **not at all** — the same cache-first discipline §3c
> has applied to `journal-s-yayinstili` since 1.10.0, with the conversation as the store instead of a
> file. A lost map (compaction) re-sends the full list rather than guessing, which is safe because
> `zotero_kutuphaneyaz.py` de-duplicates on DOI/PMID. Six sections used to mean six cold agent spawns,
> each re-reading the ~6 KB body plus 1-2 references. **§6, render: this one was not a cost, it was a
> defect.** In the default `--mode field`, `zotero_docxatifbas.py:853` guards the bibliography with
> `if not has_bibl:` — the first render writes an `ADDIN ZOTERO_BIBL` field, so every later run on that
> output reports `bibliography_count: 0` and **the second section's sources never reach the
> bibliography**. The script is honest about it (its `note` sends the user to Word's Zotero tab →
> Refresh), but §6 passed the JSON through and called the section finished. Render is now a
> **finalization** step, once per docx, fired when the section set is complete or right before
> `journalstyle`/`journalpeerreview` — which is what §7's submission order already described; the skill
> text had drifted from it. Chained renders also chained the file name (`x_zref.docx` →
> `x_zref_zref.docx`). No script changed, no component was added or removed, so the other three routing
> surfaces (`README.md`, `commands/journal.md`, `plugin.json`) are untouched by design._
>
> _Last update: 2026-09-06 — **compatibility audit: MCP · agents · references · scripts · install.**
> Three parallel read-only passes; the base held (manifest 1+4+6 exact, installed 1.16.5 = HEAD byte-for-byte
> modulo CRLF, 0 broken `${CLAUDE_PLUGIN_ROOT}` paths, 10/10 scripts parse, every documented CLI call
> matches argparse, all 26 `mcp__notebooklm-mcp__*` names in `journal-s-notebooklm` exist on the live
> server, `nlm login --check` valid, `journalresearch_pubmedara.py` answered live from NCBI). Fixed:
> (1) `zotero-r-styles.md` step 2 ordered `journal-s-zotero` to **WebFetch** the Style Repository while
> its `tools` has no web tool and `zotero-r-add-methods.md` said so — the step now hands the CSL install
> to the user and falls back to the base style; (2) the three script lines in
> `journalstyle-s-docxformat` carried no `python` prefix (a bare `.py` is not executable in Git Bash on
> Windows) and its backup step had no command — both added; (3) `zotero_kutuphaneoku.py` returned
> `no_zotero` with **exit 0**, so an exit-code check read "no library" as "empty library" — now exit 2,
> JSON body unchanged (`zotero_docxatifbas.py` parses the body, not the code, so nothing breaks);
> (4) `notebooklm-r-rehber.md` built a strategy on `chat_configure` and on "Discover sources", neither
> reachable by the agent — both marked user-side, and the `source_add` / `studio_create` enum values
> from the live schema were written next to the concepts the reference names; (5) `.gitignore` now
> covers `input/` and `*.docx` — 49 MB of the user's thesis sat untracked in the plugin root, one
> `git add .` from the repo and one `marketplace update` from every cache folder (the `*.pdf` rule's
> docx twin); (6) `journal-s-notebooklm`'s approval list gained `studio_revise`, `label`,
> `export_artifact`. Findings recorded, not fixed by code: `ZOTERO_DATA_DIR` is set at User scope but
> did not reach this Claude Code process (every read returned `no_zotero`; the same command with the
> variable exported read the library) — a restart, not a plugin change; the sync hook §1 describes is
> **not installed** on this machine and the marketplace points at GitHub, so bump/commit/push are
> manual (noted in §1); no agent can ask the user mid-run (noted in §5). No component was added or
> removed, so `README.md`, `commands/journal.md` and `plugin.json` are untouched apart from the README's
> `ZOTERO_DATA_DIR` row._
>
> _Last update: 2026-09-06 — **plugin-root raw-material model: `input/` + `output/`.** The user wanted one
> place to drop raw material (thesis docx + results xlsx + slide deck + PDFs) and one place to collect
> results; the per-docx workspace did not fit multi-file material. Two plugin-root scripts, owned by no
> skill: `scripts/hammadde_kokcoz.py` resolves the **checkout root** (env `JOURNAL_PLUGIN_HOME` → cwd
> carrying the `journal` manifest → `CLAUDE_PLUGIN_ROOT`; `no_input_root` + exit 2 like `no_zotero`) and
> scaffolds `output/`, `input/yayinstili/`, `input/authorguidelines/` — never `input/` itself, whose
> presence is the dev-checkout signal; `scripts/hammadde_oku.py` inventories `input/` (`--list`) and
> reads docx/pdf/pptx/xlsx/csv/md/txt (`--outline`, `--heading`, `--sheet`, `--pages`; python-pptx and
> openpyxl optional — zip/XML fallbacks, headings inferred from bold/numbered lines when a thesis has no
> heading style). `journalstyle_calismaklasoru.py` gained `mode: plugin-home | docx-folder` (+ `home`,
> `sources_dir`): a source under the checkout's `input/` makes the checkout the workspace with `output/`
> replacing `ciktilar/`; a source anywhere else keeps the 1.16 behaviour byte-for-byte, and an old cache
> copy without the root script still runs (import guarded). `journalresearch_pdfara.py` gained
> `--exclude DIRNAME…` so an `input/` scan skips the journal material. Every writer now targets
> `<outputs_dir>`: docxformat backup + output, `journal-s-zotero` render via `--out` when the caller
> passes `outputs_dir`, the peer-review report. Why the checkout must be resolved at all: the marketplace
> source is GitHub and `input/`/`output/` are git-ignored, so the installed copy under
> `~/.claude/plugins/cache/` never contains them (verified absent in 1.16.6). **The klasoredit S8
> warning on `output/` is accepted on purpose** — S8's premise (the whole tree is copied on install)
> holds for a local-path marketplace, not for a GitHub one; recorded in `.gitignore`, README and §2.
> No component added or removed, so `plugin.json` arrays and `marketplace.json` are untouched; the
> command's §1/§2 and every skill/agent that names a path were updated. Version 1.17.0._
>
> _Last update: 2026-09-12 — **fifth skill: `journalsunum` — academic presentation from the manuscript,
> with three sub-agents.** The user first asked for a separate presentation plugin; the scope settled on
> one skill inside this package because every presentation need was academic and the material it is
> built from already lives here. Four types: congress oral paper, congress poster, thesis defence,
> seminar / journal club / case. The skill decides narrative and slide budget, asks type · duration ·
> audience · **language every time** (no default), gets the outline approved, and renders through
> `journalsunum-s-danisman` (structure advisor, called automatically before any slide — the
> `journalwriter-s-danisman` pattern), `journalsunum-s-pptx` (deck render/edit) and
> `journalsunum-s-poster` (strict-manifest poster pipeline, fails closed, invoked twice: content hash →
> author approval → generate). **Sub-agents and references were not written from scratch:** per the
> user's direction they were found with `find-skills` and adapted from `k-dense-ai/scientific-agent-skills`
> (`scientific-slides` 1.8 + `pptx-posters` 2.2; 44.5K stars, **MIT**) — 5 references
> (`journalsunum-r-{yapi,konusma,tasarim,poster,postermanifest}.md`), the poster manifest template,
> and 11 scripts renamed by `klasoreditplugin-s-scriptadlandirma` to N12
> (`journalsunum_{manifestdogrula,gorseltara,paletdenetle,disaaktarimplanla,posteruret,pptxincele,
> yerlesimdenetle,destedogrula}.py` + libraries `journalsunum_{ortak,manifestyukle,pptxokuyaz}.py`);
> provenance header in every adapted file, MIT text in the new root `THIRD_PARTY_NOTICES.md`. Not
> taken: the upstream Nano-Banana image-generation render path and the Beamer/LaTeX material._
>
> _Two boundaries were settled in writing because they collide otherwise. (1) **The `pptx` skill is a
> machine-level, proprietary dependency**, not part of this package: the deck agent drives Anthropic's
> `anthropics/skills@pptx` (installed per machine with `npx skills add … -g`, symlinked into
> `~/.claude/skills/`), whose licence forbids copying it or deriving from it — so it is referenced, never
> shipped, and the agent returns `blocked` with the install line when it is absent. That skill's own
> description triggers on every mention of "deck/slides/presentation"; `journalsunum`'s description is
> therefore explicitly academic, and §7 plus the command's §2 now carry an "outside the plugin" row for
> generic `.pptx` mechanics, the same way statistics are routed out. (2) **Slide citations:** the strings
> come from `journal-s-zotero` and are printed as text by the render agents; the docx
> citation/bibliography authority is unchanged, and `zotero_docxatifbas.py` (python-docx) is never run
> against a `.pptx`. Also written down: the poster generator enforces exact pins (`python-pptx==1.0.2`,
> `Pillow==12.3.0`, `lxml==6.1.1` — the machine has lxml 6.1.3) and is run under `uv run --with …` so
> nothing global is downgraded; `journalsunum-s-pptx` is the first agent granted the `Skill` tool, with
> a Read-by-path fallback in its body if the harness refuses the grant. The `/journal` no-argument menu
> stays at four options (the tool's limit); presentations reach the router through "Other", which §1
> now names so a free-text answer is routed, not re-asked. A presentation is a post-submission branch,
> not a fifth pipeline step. All six surfaces moved together (§1 counts 1+5+9, §3, §3.5, new §4.5, §5,
> §6 map, §7, §10; README; command; both manifests; this file). Version **1.18.0**._
>
> _Last update: 2026-09-12 (evening) — **Office COM bridge: real PowerPoint / Word behind the render,
> verify and hand-off steps; PowerPoint Designer hand-off.** Trigger: the user installed Microsoft 365
> and asked that the plugin write to it and use its Designer. Finding first: this machine has no
> LibreOffice, and the only visual check the plugin had (`pptx` skill's `thumbnail.py` = soffice →
> pdf → pdftoppm) therefore fell to `visual_check: skipped` on every deck and poster, while nothing
> ever opened a produced `.docx`/`.pptx` in the real application. New plugin-root script
> **`scripts/office_kopru.py`** (owned by no skill): Windows PowerShell 5.1 COM sent as
> `-EncodedCommand` — no pywin32 (absent on Python 3.14, wheel status uncertain), no `.ps1` on disk
> (so the BOM rule and the `-File -Switch` pitfall never apply) — one JSON on stdout, exit 0/1/2 on
> the `no_zotero` pattern (`no_office` = exit 2, ProgID checked with `winreg` before PowerShell
> spawns). Subcommands `probe · check · render · pdf · open · fields · hunt · close`; every result
> carries `owned_instance`, `pre_pids`, `post_pids`. Verified on this machine (M365 Home Premium
> 16.0.20326): `check` (3 slides, 13.33×7.5 in, notes 1/3, `fonts_missing` caught the deliberately
> fictional face), `render` (3 PNG 1600×900 + labelled grid, Turkish glyphs intact), `pdf` (3 pages),
> Word `check`/`fields` on a fixture carrying one complex `ADDIN ZOTERO_ITEM` field (`addin_total 1`,
> `ZOTERO_ITEM 1`), Word `pdf` + `render` (pdftoppm), the broken-file path (truncated pptx →
> `com_error 0x80CB4001`, truncated docx → "Dosya bozuk görünüyor.", both exit 1, process count back
> to baseline), and `close` on a shared instance (closed only the bridge's file, `quit: false`)._
>
> _**Designer — tested, pass.** Designer has no COM API; the plan named `ExecuteMso("DesignIdeas")`
> as untested. Probe result: `GetEnabledMso('DesignIdeas')` and `'DesignIdeasPane'` raise "value out
> of range" — not idMsos; **`'DesignerPane'` is enabled and `ExecuteMso('DesignerPane')` opens the
> Tasarımcı pane** with suggestions on the current slide (PrintWindow proof captured; the bridge now
> writes such a proof PNG on every `open`). Two findings turned into rules: (1) **PowerPoint is
> single-instance** — `New-Object -ComObject` attached to the user's running PowerPoint (their deck
> open), so `Quit()` there would have closed their work; ownership is now decided from `Get-Process`
> before the COM call, and a non-owned instance is never quit (observation #155). (2) A PrintWindow
> capture from a non-DPI-aware process on a 200 % display came back as the top-left 1453×865 of a
> 2906×1730 window — the pane sat outside the crop; `SetProcessDPIAware()` fixed it (observation
> #154). Not automatable and kept manual: the Accessibility Checker's verdict (the bridge only opens
> its pane), the printer proof, CMYK, sign-off._
>
> _Wiring (all surfaces): `journalsunum-s-pptx` — probe as second action, three-tier visual pass
> (PowerPoint → LibreOffice → skipped), `fonts_missing` + note coverage in the inspection list, step 9
> Designer hand-off gated by `designer: yes|no` in the brief (default yes for congress/seminar, no on
> a user template), new "re-audit after the user's Designer edits" method (`mode: reaudit`,
> `generator_stale: true`, further edits into `_v2.pptx`), Output Format + Edge Cases;
> `journalsunum-s-poster` — the "never open with PowerPoint" line replaced by the precise rule
> (ZIP/XML `pptxincele` first, COM only after exit 0, read-only, new files only, Designer never),
> visual pass through `render --width 2400` + canvas check, new step 8 PDF export, Output Format;
> `journalsunum` SKILL step 7/8 (the *bitti / vazgeç* question and the re-invocation) + README;
> `journalstyle` step 5 Word check + Scripts; `journal-s-zotero` render job Word read-back
> (`word_check`, `match`), connection layer, Edge Cases; `zotero-r-word-flow.md` "Verification in
> Word"; `journalsunum-r-poster.md` §8/§9 and `-r-tasarim.md` §8; `journalsunum_disaaktarimplanla.py`
> gained `bridge_automatable` / `stays_manual` beside the untouched `manual_actions`; root README
> (new Office row; LibreOffice+Poppler demoted to "only without PowerPoint"); CLAUDE.md §1, §2
> (bridge paragraph), §4.1, §4.5, §5 rows, §6 map (`OFFICE` node), §7 row, §10. `commands/journal.md`
> needed no change (it names neither LibreOffice nor PowerPoint). No tool grant changed. Version
> **1.19.0** (hook still not installed — manual bump, commit, push)._
>
> _Last update: 2026-09-12 (late) — **Draft-deck mode.** The user asked whether a deck they made
> themselves, dropped into `input/pptx/`, would be taken the rest of the way. The pieces existed
> (critique mode, the render agent's edit path, the inventory already walks `input/` subfolders)
> but no flow joined them. `journalsunum` SKILL gained a "Draft-deck mode" section: read the draft
> (text dump + PowerPoint grid) → advisor fits a skeleton to it → the user chooses **polish**
> (edit path into `<stem>_v2.pptx`, draft as `--original`, `designer: no` by default) or
> **rebuild** (its content feeds the normal steps); step 1 names `input/pptx/`; the render agent's
> edit method states the `_v2` rule and the bridge-first read; README + CLAUDE.md §4.5. Not built:
> a separate template folder — a `.potx` goes in the same `input/pptx/`. Version **1.19.1**._
>
> _Last update: 2026-09-12 (night) — **The slide text budget is measured, not just advised.** The
> user asked whether the plugin knows the presentation rules — the 6×6 rule among them — and then
> asked for the numeric check. §2 of `journalsunum-r-tasarim.md` carried the numbers (bullets,
> words, font floors, line length) but nothing read them: the deck agent ran **no** package script
> at all, and the only bullet check anywhere was a vendored heuristic in `destedogrula.py` that
> counted per text frame (two boxes of five bullets passed), ignored sub-bullets, hard-coded 6, and
> skipped silently without python-pptx._
>
> _**A contradiction had to be settled before any code:** "3–4 bullets of 4–8 words is the target;
> 6×6 is the ceiling" makes the ceiling (6 words) tighter than the target (8 words). §2 now states
> it unambiguously — the ceiling is **6 bullets and 36 body words per slide** (the 6×6 product),
> a bullet over **8 words** is over target, and past roughly 60 characters it wraps._
>
> _New library `skills/journalsunum/scripts/journalsunum_metinolcer.py` (`measure_deck`,
> `summarize`): dependency-free ZIP/XML over `ppt/slides/slideN.xml`, notes resolved through each
> slide's `_rels`, reusing `pptxokuyaz`'s parser and bounds. It deliberately does **not** call
> `require_safe_pptx` — that is the one-slide poster profile, which forbids notes, hyperlinks and
> more than one slide, so every real deck fails it — and it never guesses an inherited font size
> (`FONT_SIZE_UNSPECIFIED` instead). Twelve codes at two severities, per the user's choice: target
> overruns warn (exit 0), ceilings fail (exit 1), an unreadable package is exit 2. Two findings
> came out of testing: **pptxgenjs writes no placeholders at all**, so titles were being counted as
> bullets — the title is now inferred from the slide's topmost single-line shape in the upper half
> (`title_source: inferred`) — and a title slide is identified by `ctrTitle` or by being slide 1,
> not by "carries only a title", which had promoted a mid-deck section divider._
>
> _`journalsunum_destedogrula.py` (vendored, header updated) gained the pass plus `--json`,
> `--output`, `--thresholds`, `--text-budget`/`--no-text-budget`, exit 2, and a UTF-8 stdout fix —
> its emoji report crashed outright on a Windows console codepage, which would have hit the agent
> on its first run. `--no-text-budget` reproduces the old behaviour exactly and is what the poster
> agent passes (a one-slide poster has no bullet budget). Wired into `journalsunum-s-pptx` (new
> script table, validation step 5b, the step-7 list marking which three checks are now measured,
> `text_budget:` in the Output Format, and the re-audit path since Designer re-lays out text),
> `journalsunum-s-poster`, the skill's step 8 and draft-deck mode (measured, reported, **never**
> auto-corrected), `-r-tasarim.md` §2 and §8, both READMEs, CLAUDE.md §4.5/§5/§10._
>
> _Verified: clean fixture passes with warnings; a deliberately over-budget fixture trips
> `BULLETS_OVER_CEILING`, `SLIDE_WORDS_OVER_CEILING`, `BODY_FONT_TOO_SMALL`, `NESTING_TOO_DEEP`
> and exits 1 — where the old check called the same deck merely "2 warnings, PASSED"; the user's
> own 260 MB template deck reads in 0.26 s, unmodified (mtime unchanged), reporting theme-inherited
> sizes honestly and one real 18 pt title; a truncated package exits 2. Version **1.20.0**._
