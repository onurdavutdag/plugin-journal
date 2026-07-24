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

## Contents — 5 skills + 4 agents

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

Each skill also ships its own `README.md` (task · triggers · subagents · constraints · files):
[journalstyle](skills/journalstyle/README.md) · [writer](skills/writer/README.md) ·
[research](skills/research/README.md) · [zotero](skills/zotero/README.md) ·
[peerreview](skills/peerreview/README.md).

For the full architecture reference, trigger table, and workspace model, see: **[`CLAUDE.md`](CLAUDE.md)**
(a living document — updated on every change).
