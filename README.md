# journal

A Claude Code plugin for academic/medical manuscript preparation (marketplace: `onur-plugins`).
It runs a manuscript along the **write → find sources → generate bibliography → format for the journal → critique as a reviewer**
pipeline. Documentation is in English; the skill/agent trigger descriptions are Turkish, matching the
phrases the author actually types.

## Installation

```
/plugin marketplace add onurdavutdag/journal-plugin
/plugin install journal@onur-plugins
```

## Contents — 5 skills + 5 agents

| Skill | Task |
|---|---|
| `writer` | Writes a manuscript section (Introduction/Discussion/Abstract/Conclusion) in the target journal's style; automatically calls `research` for claims that need evidence. |
| `research` | Finds real, verifiable sources (DOI/PMID) for scientific/clinical claims — never fabricates. |
| `journalstyle` | Formats a `.docx` manuscript according to the target journal's author guidelines (profile extraction → format application → citation format). |
| `zotero` | Connects to the user's real Zotero library; adds sources by DOI/PMID, writes citations/bibliography into Word. |
| `peerreview` | Evaluates a manuscript as a reviewer before submission (methodology, statistics, reporting standards). |

| Agent (subagent) | Task |
|---|---|
| `journalstyle-s-authorguidelines` | Extracts the journal's "Author Guidelines" rules from the web + a workspace PDF. |
| `journalstyle-s-yayinstili` | Examines real articles published in the journal and extracts its actual writing conventions. |
| `journalstyle-s-docxformat` | Applies mechanical `.docx` formatting (font, size, margins). |
| `writer-s-danisman` | Provides IMRaD-based writing guidance and critique before a section is written. |
| `journal-s-notebooklm` | Owns every NotebookLM interaction — advises on tool/persona/prompt and runs the `notebooklm-mcp` tools (query, studio outputs, Deep Research, source curation). Returns content, never citations. |

Each skill also ships its own `README.md` (task · triggers · subagents · constraints · files):
[journalstyle](skills/journalstyle/README.md) · [writer](skills/writer/README.md) ·
[research](skills/research/README.md) · [zotero](skills/zotero/README.md) ·
[peerreview](skills/peerreview/README.md).

For the full architecture reference, trigger table, and workspace model, see: **[`CLAUDE.md`](CLAUDE.md)**
(a living document — updated on every change).

## Conventions

- **Resource paths:** every path that crosses a component boundary (an agent reaching a skill's
  reference, one skill reaching another's) is written as
  `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/<skill>/{references,scripts}/…`. In a global install the working
  directory is the user's workspace, so bare relative paths do not resolve. A skill naming its own
  bundled resource is the one exception.
- **Reference naming:** `<owner>-r-<topic>.md` (e.g. `research-r-pdf.md`, `zotero-r-zref-protocol.md`).
- **Spec compliance:** skills follow `plugin-dev:skill-development` (third-person description with
  trigger phrases, imperative body, details in `references/`); agents follow
  `plugin-dev:agent-development` (`model` + `color` + array `tools` + a "When to invoke" section).
- **Copyright:** publisher PDFs are git-ignored and never committed; only distilled rules, metrics and
  structure enter the repository.
