---
name: journalsunum
description: >-
  Bu skill, AKADEMİK bir sunum hazırlamak için kullanılır: kongre sözlü bildirisi, kongre
  posteri, tez savunması, seminer / olgu sunumu / journal club. Kullanıcının kendi
  manuscript'inden (journalwriter çıktısı ya da input/ klasöründeki tez, docx, sonuç
  tabloları) ya da verilen bir makaleden anlatıyı kurar, slayt bütçesini süreye göre
  belirler, atıf dizelerini journal-s-zotero'dan alır, taslağı kullanıcıya onaylatır ve
  render işini alt-ajanlarına devreder (deste → journalsunum-s-pptx, poster →
  journalsunum-s-poster). Tetikleyiciler: "kongre sunumu hazırla", "bildiri sunumu",
  "poster hazırla", "70×100 poster", "tez savunması sunumu", "seminer slaytları", "journal
  club sunumu", "olgu sunumu", "makaleden sunum çıkar", "bu desteyi eleştir", "kaç slayt
  olmalı". Akademik olmayan, genel .pptx mekaniği (herhangi bir deste açmak, okumak,
  birleştirmek) bu skill'in değil global `pptx` skill'inin işidir; docx atıf/kaynakça
  journal-s-zotero'nundur.
---

# Sunum — academic presentation from manuscript to deck or poster

Build a congress talk, a poster, a thesis defence or a seminar deck from the user's own
material, in the user's language, and hand rendering to the sub-agents. This skill
decides *what* goes on the slides and gets it approved; it never draws a slide itself.

## Boundaries (read first)

- **Academic presentation work is this skill's.** Generic `.pptx` mechanics — open, read,
  merge, split a deck someone sends — belong to the global `pptx` skill, which triggers on
  its own. When a request is only "read this deck" or "merge these two files", say so in
  one line and let that skill take it.
- **Citations on slides:** the strings come from `journal-s-zotero` (agent, `Task`), printed
  as text by the render agents. The docx citation/bibliography authority
  (`commands/journal.md` §4, `CLAUDE.md` §9) is unchanged; nothing here runs
  `zotero_docxatifbas.py`, which is python-docx and cannot target a `.pptx`.
- **NotebookLM's own slide/infographic artefacts** are not this skill's output path; they
  are source material at most.
- **Nothing is fabricated:** no claim without a source in the material, no citation from
  memory, no figure redrawn from memory, no poster text the author did not approve.

## Flow

### 1. Clarify the job — no defaults

Get from the user (take what the conversation already holds; do not re-ask):

- **Type:** congress oral · poster · thesis defence · seminar / case / journal club.
- **Duration** (talks) or **organiser + printer rules** (poster: maximum size, orientation,
  delivery format, bleed/margins, colour mode — with where each rule came from).
- **Audience** and whether **Q&A is inside the slot**.
- **Language** of the slides (TR / EN) — asked, never assumed from the material.
- **Source material.** Run
  `PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/hammadde_oku.py" --list`
  and offer the checkout's `input/` inventory (docx · pdf · pptx · xlsx/csv · md/txt); a
  `no_input_root` JSON (exit 2) means `JOURNAL_PLUGIN_HOME` must point at the checkout root
  — say so, then ask for a path. For a journal club, the source is the paper (PDF) and the
  user's notes.
- **Citation style** for slide references: the journal profile's `citation_style` if a
  manuscript with a profile exists, otherwise ask (Vancouver is the usual congress default).

Ask with one `AskUserQuestion` per missing group, not one per field.

### 2. Resolve the workspace

`PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/journalstyle_calismaklasoru.py" "<source file>"`
— use the returned `mode`, `sources_dir`, `outputs_dir`; never a literal `output/` or
`ciktilar/`. Outputs: `<outputs_dir>/<stem>_sunum.pptx` (deck), `<stem>_poster.pptx` and
`poster.json` (poster), plus the generator script and preview grids beside them. `input/`
is never written.

### 3. Read the material

`hammadde_oku.py "<file>"` (`--outline`, `--heading`, `--sheet`, `--pages` to narrow);
`skills/journalstyle/scripts/journalstyle_docxyapicikar.py` for a manuscript's structure.
Note the 1–3 core messages, the figures and tables that carry them, and every claim that
will need a reference on a slide.

### 4. Structure — call the advisor automatically

**Before drafting any slide, call `journalsunum-s-danisman` with the `Task` tool** (do not
wait for approval), passing: type · duration · audience · Q&A placement · language · the
material's outline and the candidate messages · an existing deck's text dump if the job is
a critique. What comes back is defined in the agent's **"Output Format"**: budget, skeleton,
citation slots, reminders, practice minimum (+ critique). Do not restate the contract here.

### 5. Sources for the slides

- **Citation slots** from the skeleton → one `journal-s-zotero` call (`Task`) with the list
  of sources (DOI/PMID/title) and the style; it returns formatted strings (and adds missing
  items to the library only with the user's approval, as its own contract says). Keep the
  map; send only deltas on later passes.
- **Unsourced claim** that must appear on a slide → `journalresearch` (skill) first, then
  the zotero call. Never type a reference from memory.
- **Seminar / journal club / literature deck** → `journal-s-notebooklm` (`Task`) following
  **"Call procedure"** in `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/notebooklm-r-rehber.md`;
  what it returns is content to verify, never a citation.

### 6. Draft and approve the outline

Write the outline in the user's language and voice: for every slide — number · title · the
one message · body text (≤ 4 bullets, ≤ 8 words each) · the visual (which figure/table,
simplified how) · speaker note (the sentence the slide exists to say + the transition) ·
citation strings to print. Backup slides after the last slide, each with the question it
answers. Apply the user's global number/percentage/p-value format (TR comma and `%`
before, EN period and `%` after).

Show it and **get explicit approval** (`AskUserQuestion`: approve / change / add / remove).
Nothing is rendered before that yes.

**Poster:** instead of an outline, assemble the **evidence packet**
(`journalsunum-r-poster.md` §4): exact title/authors/affiliations/contact, the approved
section texts, figures as local PNG/JPEG with captions, reference strings, organiser and
printer rules with sources, QR target. Get the user's approval of every text verbatim —
the poster agent renders exact text and will refuse anything unapproved.

### 7. Render — hand to the sub-agent

- **Deck:** `journalsunum-s-pptx` (`Task`) with the approved outline, the design choices
  (palette for the topic, fonts, 16:9 or the user's template), the citation strings,
  `outputs_dir`, the stem and **`designer: yes | no`** — `yes` by default for a congress or
  seminar deck, `no` when the user supplied their own template (PowerPoint Designer
  rewrites layouts) or asked for none. It returns the JSON block in its "Output Format":
  file path, validation, `office` (PowerPoint found or not), visual-check result, remaining
  issues, `designer_handoff`. If it returns `blocked: pptx skill not installed`, relay the
  fix line to the user verbatim — the skill is a machine-level dependency (README →
  Requirements).
  - **`designer_handoff: opened`** → PowerPoint is on the user's screen with the Designer
    ("Tasarımcı") pane open on the finished deck. Tell them so, in one line: pick a design per
    slide, **save**, come back. Ask (`AskUserQuestion`: *bitti / vazgeç / şimdi değil*).
    On *bitti*, re-invoke `journalsunum-s-pptx` with `mode: reaudit` and the same path; its
    report (`generator_stale: true`) replaces the first one. On *vazgeç* the first report
    stands and the deck as generated is the deliverable.
  - `opened_no_pane` → the deck is open; the user reaches Designer from the Design tab.
- **Poster:** `journalsunum-s-poster` (`Task`) with the packet and `outputs_dir`. First
  pass returns `needs_approval` with the manifest path and the content hash — show both to
  the user, get approval, then re-invoke with the approval fields; it then runs the full
  pipeline and returns status, output path, `pdf` (exported through PowerPoint when it is
  installed and the export plan has no blocker, else `manual`) and the checklist state.
  Items it marks `manual` (PowerPoint Accessibility Checker, printer proof, author sign-off)
  are handed to the user as their steps, never claimed. Designer is never offered for a poster.

### 8. Report

One block: what was produced (path), slide/backup count or poster geometry, what was
verified (validate · visual pass — through PowerPoint, through LibreOffice, or skipped and
why · package/layout audits · PDF export), the Designer hand-off state, what remains manual,
and the practice minimum from the advisor. Offer the next step in the same line: a critique
pass on the rendered deck, the poster's PDF / print proof, or a lightning version.

## Critique mode

"Bu desteyi eleştir" / "yayına hazır mı bu sunum": read the deck through
`journalsunum-s-pptx` (text dump + grid), pass both to `journalsunum-s-danisman`, return
its critique and the pitfall findings; edit only if the user asks, through the render
agent's edit path.

## Sub-agent routing table

| Job | Agent | Called |
|---|---|---|
| structure, budget, skeleton, critique | `journalsunum-s-danisman` | automatically, before any slide |
| deck render / edit / read | `journalsunum-s-pptx` | after outline approval |
| poster manifest, generation, audits | `journalsunum-s-poster` | after packet approval; twice (hash → approval → generate) |
| citation strings for slides | `journal-s-zotero` | when the skeleton names citation slots |
| literature for seminar / journal club | `journal-s-notebooklm` | per `notebooklm-r-rehber.md` |
| unsourced claim | `journalresearch` (skill) | before the zotero call |

**Delegation rule (critical):** every path in a brief is absolute —
`${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalsunum/...` — because the sub-agent's working
directory is the user's workspace. Approval gates live here, not in the agents: a question
an agent returns is asked by this skill and the agent is re-invoked.

## Files

- `references/journalsunum-r-yapi.md` — narrative arc, manuscript → slide mapping, skeletons.
- `references/journalsunum-r-konusma.md` — the four oral types as parameter sets; timing,
  Q&A, backup, practice.
- `references/journalsunum-r-tasarim.md` — slide design invariants, typography, colour,
  layout, figures, pitfall checklist.
- `references/journalsunum-r-poster.md` — poster requirements, geometry, content rules,
  accessibility, release checklist.
- `references/journalsunum-r-postermanifest.md` + `journalsunum-poster-manifest-ornek.json`
  — the poster manifest schema and its deliberately invalid template.
- `scripts/journalsunum_*.py` — the poster pipeline (validate · inventory · palette · export
  plan · generate · inspect · layout) and a deck sanity check; run by the poster agent.
- `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/office_kopru.py` (plugin root, owned by no skill) —
  the Microsoft Office bridge the two render agents call: slide PNG + grid through real
  PowerPoint, PDF export, font-substitution check, the visible Designer hand-off. Optional:
  exit 2 `no_office` selects the LibreOffice / manual path.

Adapted from `k-dense-ai/scientific-agent-skills` (MIT) — provenance headers in each file,
licence in the root `THIRD_PARTY_NOTICES.md`.
