# journal

A Claude Code plugin for academic/medical manuscript preparation (marketplace: `plugin-journal`).
It runs a manuscript along the **write → find sources → generate bibliography → format for the journal → critique as a reviewer**
pipeline. Documentation is in English; the skill/agent trigger descriptions are Turkish, matching the
phrases the author actually types.

## Installation

```
/plugin marketplace add onurdavutdag/plugin-journal
/plugin install journal@plugin-journal
```

### Requirements

| What | Why · how it is resolved |
|---|---|
| **Python 3** + `python-docx` | Every `.docx` operation — formatting (`journalstyle_docxbicimuygula.py`) and the citation/bibliography render (`zotero_docxatifbas.py`). |
| **Zotero** (only for `journal-s-zotero`) | Reading the library uses `zotero.sqlite` and **works with Zotero closed**. **Writing** a new record needs **Zotero 7 running**, because it goes through the local connector API at `http://127.0.0.1:23119`; `zotero.sqlite` is never written to. |
| `ZOTERO_DATA_DIR` (env var, optional) | Where the Zotero data directory lives. Unset → `~/Zotero`. Set it if Zotero was installed to a custom path, otherwise `zotero_kutuphaneoku.py` reports `no_zotero` (exit 2). A value set in Windows reaches only Claude Code processes started **after** it was set — restart the terminal/app. |
| `JOURNAL_PLUGIN_HOME` (env var, recommended) | The plugin-journal **checkout root** — the folder holding `input/` and `output/` (see "Raw material and outputs"). The installed copy under `~/.claude/plugins/cache/` never contains those folders (git-ignored), so `scripts/hammadde_kokcoz.py` resolves the checkout at run time: this variable → the current directory if it is the checkout → `CLAUDE_PLUGIN_ROOT`. Unset and not run from the checkout → `no_input_root` (exit 2) and the skills ask for a file path instead. Same restart caveat as `ZOTERO_DATA_DIR`. |
| **Anthropic `pptx` skill** (only for `journalsunum` decks) | `journalsunum-s-pptx` drives it to write, validate and preview the `.pptx`. It is **proprietary and not shipped here** — install it per machine: `npx skills add anthropics/skills@pptx -g`, then `npm install -g pptxgenjs` (or `npm install pptxgenjs` in the output folder) and `python -m pip install "markitdown[pptx]"`. Its own slide-grid preview needs LibreOffice + Poppler (`soffice`, `pdftoppm`) on `PATH` — **only when Microsoft PowerPoint is not installed** (next row). Missing skill → the agent stops with that install line; nothing else in the plugin needs it. |
| **Microsoft Office — PowerPoint, Word** (optional) | `scripts/office_kopru.py` drives them through **PowerShell COM** (no pip package, no env var): slide PNGs + labelled grid from real PowerPoint, PDF export, font-substitution check, Word field census for the Zotero render, and the visible **Designer hand-off** (the finished deck opens on screen with the Designer pane; the user picks, saves, the plugin re-audits). Detected at run time from the `PowerPoint.Application` / `Word.Application` ProgIDs; absent → `{"error": "no_office"}` (exit 2) and each caller falls back (LibreOffice preview) or marks the step manual. PowerPoint is single-instance: when the user's own PowerPoint is open the bridge attaches to it, works invisibly and never quits it. |
| `uv` (only for `journalsunum` posters) | The poster generator enforces exact pins (`python-pptx==1.0.2`, `Pillow==12.3.0`, `lxml==6.1.1`); `journalsunum-s-poster` runs it under `uv run --with …` so the machine's packages are never downgraded. The audit scripts run under the normal Python. |
| `python-pptx`, `openpyxl` (optional) | Better `.pptx` / `.xlsx` reading in `scripts/hammadde_oku.py`. Without them the reader falls back to the files' own zip/XML (text, notes and cached cell values still come out; formulas without a cached result and shape order are lost) and says so in its `warnings`. |
| `NCBI_EMAIL`, `NCBI_API_KEY` (env vars, optional) | Politeness headers for NCBI E-utilities (`journalresearch_pubmedara.py`). Neither is required — the public API needs no authentication. |
| `pypdf` or `pymupdf` (optional) | Reading sample-article PDFs for the publication-style analysis; without it that step falls back to the web. |

MCP connectors (NotebookLM, Consensus, PubMed) are **optional**: the plugin defines no MCP server
of its own, and each path degrades to a non-MCP fallback — PubMed to `journalresearch_pubmedara.py`, the
literature pool to the local `pdflerim/` folder.

## Usage

Every skill triggers on its own natural-language phrasing ("tartışma bölümünü yaz", "bu makale yayına
hazır mı"). When it is unclear which one is needed, use the single entry point:

```
/journal tartışma bölümünü yaz, hedef dergi The Spine Journal
/journal makale.docx dosyasını MDPI için hazırla
/journal                     # no argument → asks what the job is, then routes
```

`/journal` only routes: it reads the request, picks the owning skill (or one of the two directly
callable agents — `journal-s-zotero`, `journal-s-notebooklm`), collects what that owner needs and hands
over. For a full run it chains
journalwriter → journal-s-zotero → journalstyle → journalpeerreview, asking for approval between steps.

## Raw material and outputs — `input/` and `output/`

Two folders at the checkout root (both git-ignored, both created on demand):

- **`input/`** — drop the raw material here: the thesis or draft `.docx`, a results workbook
  (`.xlsx`/`.csv`), a slide deck (`.pptx`), PDFs, notes (`.md`/`.txt`). The skills use them
  according to your instruction ("write the Discussion from the thesis and the results sheet").
  `input/yayinstili/<slug>/` and `input/authorguidelines/<slug>/` hold the target journal's sample
  articles and author guidelines, with the extracted profiles beside them.
- **`output/`** — everything the plugin produces lands here: the formatted `.docx`, the
  `_zref.docx` render with citations, backups, the peer-review report. Evaluate the results from
  this folder; `input/` is never modified.

`scripts/hammadde_oku.py --list` inventories `input/`; `scripts/hammadde_oku.py "<file>"` returns the
content of any supported file (`--outline`, `--heading`, `--sheet`, `--pages` narrow it). When a source
`.docx` lives elsewhere, the previous per-folder workspace (`yayinstili/`, `authorguidelines/`,
`ciktilar/` beside the file) still applies — `journalstyle_calismaklasoru.py` reports which mode it
chose. The `output/` folder inside a plugin tree trips klasoredit's **S8** warning; it is accepted on
purpose here, because the marketplace source is GitHub and the folder never reaches an installed copy.

## Contents — 1 command + 5 skills + 9 agents

| Command | Task |
|---|---|
| `/journal` | Single entry point: works out which skill/agent owns the request, collects the required information and hands the job over. Writes/formats/cites nothing itself. |

| Skill | Task |
|---|---|
| `journalwriter` | Writes a manuscript section (Introduction/Methods/Results/Discussion/Abstract/Conclusion) in the target journal's style; automatically calls `journalresearch` for claims that need evidence. |
| `journalresearch` | Finds real, verifiable sources (DOI/PMID) for scientific/clinical claims — never fabricates. |
| `journalstyle` | Formats a `.docx` manuscript according to the target journal's author guidelines (profile extraction → format application → verification). Does not touch citations or the bibliography — it hands that to `journal-s-zotero`. |
| `journalpeerreview` | Evaluates a manuscript as a reviewer before submission (methodology, statistics, reporting standards). |
| `journalsunum` | Builds an **academic presentation** — congress oral paper, congress poster, thesis defence, seminar / journal club — from the user's own material: narrative and slide budget, outline approved by the user, rendering handed to its sub-agents. Asks type, duration, audience and language every time. Generic `.pptx` mechanics stay with the global `pptx` skill. |

| Agent (subagent) | Task |
|---|---|
| `journal-s-authorguidelines` | Extracts the journal's "Author Guidelines" rules from the web + a workspace PDF. |
| `journal-s-yayinstili` | Examines real articles published in the journal and extracts its actual writing conventions. |
| `journalstyle-s-docxformat` | Applies mechanical `.docx` formatting (font, size, margins). |
| `journalwriter-s-danisman` | Provides IMRaD-based writing guidance and critique before a section is written. |
| `journal-s-zotero` | **Owns everything that touches the real Zotero library**: queries it, has sources added by DOI/PMID, writes in-text citations + the bibliography into a `.docx`, converts the style, pins citations. The docx bibliography is its authority alone. `journalwriter`, `journalstyle` and `journalpeerreview` delegate to it; it runs in its own context so library dumps never reach the conversation. See **Requirements** above for the Zotero prerequisites. |
| `journal-s-notebooklm` | Owns every NotebookLM interaction — advises on tool/persona/prompt and runs the `notebooklm-mcp` tools (query, studio outputs, Deep Research, source curation). Returns content, never citations. |
| `journalsunum-s-danisman` | Presentation structure advisor: slide budget for type + duration, skeleton slide by slide, backup slides, citation slots, timing checkpoints; critiques an existing deck. Writes no slide, produces no citation. |
| `journalsunum-s-pptx` | Renders the approved outline to a `.pptx` (and edits / reads existing decks) by driving the machine-level Anthropic `pptx` skill; validates the file and inspects the slide grid as an image — rendered by real PowerPoint when it is installed — before reporting; then opens the deck on screen with the Designer pane for the user and re-audits what they saved. |
| `journalsunum-s-poster` | Writes the strict poster manifest from the approved evidence packet, returns the content hash for author approval, then runs the poster pipeline (validate · inventory · palette · export plan · generate · package inspection · layout), previews and exports the PDF through PowerPoint once the package inspection has passed. Fails closed; never fabricates; never runs Designer on a poster. |

Each skill also ships its own `README.md` (task · triggers · subagents · constraints · files):
[journalstyle](skills/journalstyle/README.md) · [journalwriter](skills/journalwriter/README.md) ·
[journalresearch](skills/journalresearch/README.md) · [journalpeerreview](skills/journalpeerreview/README.md) ·
[journalsunum](skills/journalsunum/README.md).

For the full architecture reference, trigger table, and workspace model, see: **[`CLAUDE.md`](CLAUDE.md)**
(a living document — updated on every change).

## Conventions

- **Resource paths:** every path that crosses a component boundary (an agent reaching a skill's
  reference, one skill reaching another's) is written as
  `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/<skill>/{references,scripts}/…` — or `.../{references,scripts}/…`
  at the plugin root for what no skill owns (the zotero scripts and references, the NotebookLM guide).
  In a global install the working
  directory is the user's workspace, so bare relative paths do not resolve. A skill naming its own
  bundled resource is the one exception.
- **Reference naming:** `<owner>-r-<topic>.md` (e.g. `journalresearch-r-pdf.md`, `zotero-r-zref-protocol.md`).
- **Spec compliance:** skills follow `plugin-dev:skill-development` (third-person description with
  trigger phrases, imperative body, details in `references/`); agents follow
  `plugin-dev:agent-development` (`model` + `color` + array `tools` + a "When to invoke" section).
- **Copyright:** **no publisher PDF is kept inside the plugin's shipped tree** — sample articles and
  author guidelines live in the user's workspace (next to the source `.docx`, or under the checkout's
  git-ignored `input/`). `.gitignore` blocks `*.pdf`, `*.docx`, `*.pptx`, `*.xlsx`, `input/` and
  `output/`; because the marketplace source is GitHub, what git ignores never reaches an installed
  copy. Only distilled rules, metrics and structure enter the repository.
