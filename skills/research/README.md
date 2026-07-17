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
2. **PDFs uploaded to the current project/workspace** — your own library is preferred.
3. **Consensus / PubMed search** — only when 1 and 2 don't cover the claim.

For external evidence it prefers, in order: systematic reviews/meta-analyses → RCTs →
prospective observational → retrospective, using landmark studies when they remain the
standard and favoring recent work otherwise.

## The never-fabricate guarantee

Every reference is real and verifiable — a resolvable DOI/PMID retrieved from PubMed/Consensus,
or a passage located in an actual uploaded PDF (with page number). If nothing reliable is found,
the skill says so plainly rather than inventing a source.

## Output (per recommendation)

Supported sentence · Recommended reference(s) · Why selected · Evidence level ·
Source (User-provided reference / Uploaded PDF / Consensus) · Page number (if PDF) · DOI ·
PMID (if available). Default citation style: **Vancouver**.

## Triggering it

It auto-triggers on unsupported empirical claims and on requests to find/verify/add/format
references. To invoke it explicitly, type `/research`, or ask e.g. "find a citation for this
sentence" or "search my PDFs for evidence on X".

## Dependencies

- **Consensus** and **PubMed** connectors (already available in this account) for external search.
- Optional: `pip install pypdf` so `scripts/search_pdfs.py` can extract PDF text. Without it,
  Claude falls back to reading PDFs directly with the Read tool.
- Elicit is optional and requires separate authorization; not needed.

## Files

```
research/
├── SKILL.md                       # skill definition + workflow (auto-loaded)
├── README.md                      # this file
├── LICENSE.txt
├── references/
│   ├── research-r-pdf.md          # finding & searching uploaded PDFs
│   ├── research-r-consensus.md    # Consensus/PubMed, study hierarchy, evidence levels
│   └── research-r-kunye.md        # mandatory output template + examples
└── scripts/
    └── search_pdfs.py             # keyword/phrase search across workspace PDFs
```
