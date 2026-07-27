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

## Contents — 1 command + 4 skills + 6 agents

| Command | Task |
|---|---|
| `/journal` | Single entry point: works out which skill/agent owns the request, collects the required information and hands the job over. Writes/formats/cites nothing itself. |

| Skill | Task |
|---|---|
| `journalwriter` | Writes a manuscript section (Introduction/Methods/Results/Discussion/Abstract/Conclusion) in the target journal's style; automatically calls `journalresearch` for claims that need evidence. |
| `journalresearch` | Finds real, verifiable sources (DOI/PMID) for scientific/clinical claims — never fabricates. |
| `journalstyle` | Formats a `.docx` manuscript according to the target journal's author guidelines (profile extraction → format application → verification). Does not touch citations or the bibliography — it hands that to `journal-s-zotero`. |
| `journalpeerreview` | Evaluates a manuscript as a reviewer before submission (methodology, statistics, reporting standards). |

| Agent (subagent) | Task |
|---|---|
| `journal-s-authorguidelines` | Extracts the journal's "Author Guidelines" rules from the web + a workspace PDF. |
| `journal-s-yayinstili` | Examines real articles published in the journal and extracts its actual writing conventions. |
| `journalstyle-s-docxformat` | Applies mechanical `.docx` formatting (font, size, margins). |
| `journalwriter-s-danisman` | Provides IMRaD-based writing guidance and critique before a section is written. |
| `journal-s-zotero` | **Owns everything that touches the real Zotero library**: queries it, has sources added by DOI/PMID, writes in-text citations + the bibliography into a `.docx`, converts the style, pins citations. The docx bibliography is its authority alone. `journalwriter`, `journalstyle` and `journalpeerreview` delegate to it; it runs in its own context so library dumps never reach the conversation. |
| `journal-s-notebooklm` | Owns every NotebookLM interaction — advises on tool/persona/prompt and runs the `notebooklm-mcp` tools (query, studio outputs, Deep Research, source curation). Returns content, never citations. |

Each skill also ships its own `README.md` (task · triggers · subagents · constraints · files):
[journalstyle](skills/journalstyle/README.md) · [journalwriter](skills/journalwriter/README.md) ·
[journalresearch](skills/journalresearch/README.md) · [journalpeerreview](skills/journalpeerreview/README.md).

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
- **Copyright:** **no publisher PDF is kept inside the plugin tree** — sample articles and author
  guidelines live in the user's workspace, next to the source `.docx`. `.gitignore` blocks `*.pdf` as a
  second line of defence, but it is not sufficient on its own: `marketplace update` + `install` copy the
  whole tree, so a PDF left in the plugin is replicated into every installed version folder. Only
  distilled rules, metrics and structure enter the repository.
