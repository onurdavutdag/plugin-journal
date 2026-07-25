<!-- Güncelleme: 20260725 0056 -->
# research — Academic Citation Assistant

A Claude Code skill that helps you write manuscripts by supplying **real, verifiable**
references for your scientific and clinical claims. It **never fabricates citations**.

## What it does

When a paragraph you (or Claude) just wrote or revised makes an empirical claim that needs
evidence and you didn't already supply a citation, this skill activates **automatically** —
no confirmation prompt — finds supporting references, and reports them in a fixed format with
DOI/PMID and a one-line justification for each.

## Evidence priority

1. **References you explicitly supplied** (in the conversation or project).
2. **PDFs uploaded to the current project/workspace** — your own library is preferred. The fixed
   `pdflerim/` library is scanned on **every** citation task, in addition to the workspace scan.
3. **NotebookLM notebooks** — delegated to the `journal-s-notebooklm` agent, which owns all
   NotebookLM interaction. A *finding* layer only; every paper it surfaces is still verified
   through PubMed/DOI before it may be cited.
4. **Consensus / PubMed search** — only when tiers 1–3 don't cover the claim.

For external evidence it prefers, in order: systematic reviews/meta-analyses → RCTs →
prospective observational → retrospective, using landmark studies when they remain the
standard and favoring recent work otherwise.

## The never-fabricate guarantee

Every reference is real and verifiable — a resolvable DOI/PMID retrieved from PubMed/Consensus,
or a passage located in an actual uploaded PDF (with page number). If nothing reliable is found,
the skill says so plainly rather than inventing a source.

## Output (per recommendation)

Supported sentence · Recommended reference(s) · Why selected · Evidence level ·
Source (User-provided reference / Uploaded PDF / NotebookLM notebook / Consensus) ·
Page number (if PDF) · DOI · PMID (if available).

**Formatting is not this skill's job:** the in-text citation format and the docx bibliography belong
to the `zotero` skill alone. research returns the verified record; `zotero` renders it.

## Triggering it

It auto-triggers on unsupported empirical claims and on requests to find/verify/add/format
references. To invoke it explicitly, type `/research`, or ask e.g. "find a citation for this
sentence" or "search my PDFs for evidence on X".

## Dependencies

- **Consensus** and **PubMed** connectors (already available in this account) for external search.
  If they are not authorized, `scripts/pubmed_eutils.py` queries the public NCBI E-utilities API
  with **no auth** — the flow never stops and never fabricates.
- Optional: `pip install pypdf` so `scripts/search_pdfs.py` can extract PDF text. Without it,
  Claude falls back to reading PDFs directly with the Read tool.
- Optional: the `notebooklm-mcp` server for tier 3 (`nlm login` refreshes an expired session).
  If it is absent, the tier is skipped silently.
- Elicit is optional and requires separate authorization; not needed.

## Subagents

| Called | When | Purpose |
|---|---|---|
| `journal-s-notebooklm` | tier 3, when tiers 1–2 don't cover the claim | resolves the notebook and queries it; returns grounded findings + the studies this skill must then verify |

`writer` calls *this* skill in return, for every evidence-needing claim without a user citation.

## Files

```
research/
├── SKILL.md                       # skill definition + workflow (auto-loaded)
├── README.md                      # this file
├── references/
│   ├── research-r-pdf.md          # finding & searching uploaded PDFs
│   ├── research-r-consensus.md    # Consensus/PubMed, study hierarchy, evidence levels
│   └── research-r-kunye.md        # mandatory output template + examples
├── pdflerim/                      # your fixed PDF library — scanned on every task
└── scripts/
    ├── search_pdfs.py             # keyword/phrase search across workspace PDFs
    └── pubmed_eutils.py           # no-auth NCBI E-utilities fallback
```

Scripts are always invoked with `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/research/scripts/...` — in a
global install the working directory is the study workspace, so a relative `scripts/...` path breaks.
