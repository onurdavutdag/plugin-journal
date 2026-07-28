# External evidence — Consensus & PubMed

Use these **only when tiers 1–2 fail** (the user's supplied references and their uploaded
PDFs do not cover the claim). The goal is a real, verifiable reference with a DOI and/or
PMID — never a remembered or reconstructed one.

## Study-type hierarchy → evidence level

Prefer the strongest design available for the claim. Report the level in the output's
`Evidence level` field.

| Level | Study design | Notes |
|:---:|---|---|
| **1** | Systematic review / meta-analysis | Highest; prefer when it exists and is on-point |
| **2** | Randomized controlled trial (RCT) | Best single-study causal evidence |
| **3** | Prospective observational (cohort) | When RCTs are absent/unethical |
| **4** | Retrospective / case-control | Lower; note residual confounding |
| **5** | Mechanistic, case series, expert/guideline consensus | Use for background or when nothing higher exists |

**Landmark studies**: cite a landmark trial/paper when it remains the accepted standard for
the claim even if older (e.g., a seminal RCT that defines current practice).

**Recency**: otherwise prefer recent evidence — newer meta-analyses and guidelines supersede
older ones. Recency does not override a canonical landmark reference.

## Consensus

`mcp__claude_ai_Consensus__search` — pass just the `query` (a clear research question)
unless the user explicitly asks to filter by year, study type, sample size, etc. Do NOT add
filters on your own.

Comply with the Consensus MCP output rules: cite returned papers inline by their numbered
references (`[1]`, `[2]`), attribute findings to specific papers, list cited papers at the
end with titles hyperlinked to the exact URLs from the tool result (do not modify the URLs),
and include the tool result's sign-up/upgrade/usage message **verbatim** at the end of that
response. Batch at most 3 search calls at a time; wait 30 s if rate-limited.

## PubMed

Use the `mcp__claude_ai_PubMed__*` tools to find and, crucially, **verify** references and
recover identifiers:

- `search_articles` — find candidate papers by topic/question.
- `get_article_metadata` — pull authors, title, journal, year, volume/issue/pages, DOI, PMID.
- `convert_article_ids` — map between PMID / PMCID / DOI.
- `lookup_article_by_citation` — resolve a partial citation (title + authors + year) to a
  PMID/DOI; use this to fill a DOI/PMID missing from an uploaded PDF.
- `find_related_articles` — broaden to systematic reviews or related trials.

Always confirm the returned DOI/PMID actually corresponds to the paper you're citing before
putting it in the output.

## No-auth fallback — NCBI E-utilities (when the MCP connectors aren't authorized)

The `mcp__claude_ai_PubMed__*` and `mcp__claude_ai_Consensus__*` tools require OAuth via
claude.ai connector settings and are **unavailable in non-interactive sessions**. When they
are not connected, do **not** stop and do **not** fabricate — fall back to the bundled
`scripts/journalresearch_pubmedara.py`, which queries the public NCBI E-utilities REST API. It needs no
authentication and no API key, and returns the same real, verifiable records (title, authors,
journal, year, volume/issue/pages, **DOI**, **PMID**, URL).

```
PLUGIN="${CLAUDE_PLUGIN_ROOT:-$(pwd)}"
python "$PLUGIN/skills/journalresearch/scripts/journalresearch_pubmedara.py" --query "clear research question / keywords" --retmax 5
python "$PLUGIN/skills/journalresearch/scripts/journalresearch_pubmedara.py" --pmid 34567890                 # verify / expand one record
python "$PLUGIN/skills/journalresearch/scripts/journalresearch_pubmedara.py" --doi 10.1001/jama.2019.4783    # resolve a DOI to its record
```

Use it exactly like the PubMed MCP path — apply the same study-type hierarchy, recency vs.
landmark judgement, and the "confirm the DOI/PMID matches the paper" rule before citing. It
covers `search_articles`, `get_article_metadata`, `convert_article_ids`, and
`lookup_article_by_citation` (search by title/author text) equivalently.

Fallback limits, and when to tell the user to authorize:
- **PubMed only.** There is no free no-auth Consensus equivalent. If a claim genuinely needs
  Consensus-style evidence synthesis that PubMed cannot cover, tell the user to authorize the
  Consensus connector in their claude.ai connector settings in an interactive session.
- If the script returns `{"error": "eutils_unreachable"}` (network blocked), report that and
  tell the user to authorize the PubMed/Consensus MCP connector — don't invent a citation.
- Prefer the MCP tools when they *are* authorized; the script is the fallback, not the default.

## Elicit (optional)

The Elicit connector may be useful for evidence synthesis but **requires authorization** and
is not connected in non-interactive sessions. Do not depend on it; Consensus + PubMed suffice.
If the user wants Elicit, tell them to authorize it in their claude.ai connector settings.
