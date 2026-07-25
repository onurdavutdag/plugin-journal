---
name: research
description: >-
  This skill is the academic research and citation assistant for manuscript writing: it
  finds real, verifiable references (DOI/PMID) supporting scientific or clinical claims
  and NEVER fabricates citations. It should be used AUTOMATICALLY — without asking for
  confirmation — whenever a newly written or revised paragraph makes a scientific,
  medical, statistical, or clinical claim that needs an evidence citation and the user
  supplied none. It should also be used whenever the user asks to find, add, verify, or
  strengthen references; check whether a statement is supported by the literature; search
  their uploaded PDFs for evidence; or look something up on PubMed or Consensus.
  (FORMATTING citations/bibliography in a docx belongs to `zotero`.) It triggers even if
  the words "citation" or "reference" are never said — an unsupported empirical claim in a
  manuscript is enough. Keywords: citation, reference, evidence, PubMed, Consensus,
  meta-analysis, RCT, DOI, PMID, manuscript, literature.
version: 0.1.0
---

# research — Academic Citation Assistant

Help a medical researcher write manuscripts by supplying **real, verifiable**
references that support their claims. This is a trust-critical job: a single fabricated
citation can sink a paper and the author's credibility.

## Prime directive — never fabricate

**Every proposed reference must be real and independently verifiable.** That means
either:
- a resolvable **DOI** and/or **PMID** actually retrieved from PubMed/Consensus, or
- a passage actually located inside an uploaded PDF (with page number).

If a paper's existence cannot be verified, **do not cite it**. Never invent authors, titles,
journals, years, DOIs, or PMIDs, and never "reconstruct" a citation from memory. If no
reliable evidence is found, **say so explicitly** — that is a correct and valuable answer.
A missing citation is fine; a fake one is not.

## When to invoke (automatically, no confirmation)

Invoke this skill the moment a freshly written or revised paragraph asserts an empirical,
clinical, epidemiological, or statistical claim with no citation the user supplied — for
example incidence/prevalence figures, treatment effects, mechanism statements, "X is
associated with Y", guideline recommendations, or comparative outcomes. Also invoke when
the user directly asks to find/verify/add references.

While working:
- Operate automatically — don't stop to ask "should I find a citation?" Just do it.
- **Identify the exact sentence(s)** each suggested citation supports.
- **Preserve the manuscript's wording and style.** Suggest references; do not
  rewrite the author's prose unless asked.

## Evidence priority (strict order)

Search in this order and only descend a tier when the current tier lacks suitable support:

1. **References the user explicitly supplied** — in this conversation or the project. Use
   these first; they are the author's chosen literature.
2. **PDFs uploaded to the current project/workspace** — the author's own library. Prefer
   citing these whenever they genuinely support the statement.
3. **NotebookLM notebooks** — the author's curated literature pool, reached through the
   `journal-s-notebooklm` agent (never by calling the MCP tools here). A *finding* layer only;
   every paper it surfaces must still be verified (see Step 1b).
4. **Consensus / PubMed search** — only when tiers 1–3 do not yield suitable evidence.

## Step 1 — Search uploaded references and PDFs

Before any external search, exhaust the user's own material.

**Always scan the fixed `pdflerim/` library first.** This skill ships a `pdflerim/` folder in its
own directory where the author drops their curated PDFs; scan it on every citation task (in
addition to the general workspace scan), before any external search. If it's empty, skip silently.
See `references/research-r-pdf.md` step 0.

Run the bundled searcher over every PDF in the project/workspace:

```
python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/research/scripts/search_pdfs.py" --dir <workspace-or-project-dir> --terms "keyword" "phrase" ...
```

(`${CLAUDE_PLUGIN_ROOT}` gives the plugin root; in a global install cwd is the workspace, so scripts
are called with this variable — a relative `scripts/...` path breaks globally.)

It returns JSON hits `{file, page, section_heading, snippet}`. For each promising hit, open
the PDF at that page with the **Read tool** (`pages` parameter) to confirm and read context.
Then:
- **Report the page number and section heading** whenever available.
- **Summarize** the supporting evidence in fresh wording instead of copying long text.
- **Quote only the minimum text necessary** to establish the point.

See `references/research-r-pdf.md` for discovery (including Google Drive PDFs), hit
interpretation, and passage-extraction rules.

## Step 1b — NotebookLM notebooks (only if tiers 1–2 fail)

The user keeps a curated literature pool in Google NotebookLM. **Do not call the MCP tools
here** — every NotebookLM interaction in this plugin belongs to the `journal-s-notebooklm`
agent. **Call it with the Agent tool** and give it a brief.

- **The brief to pass:** the claim/sentence needing support · the manuscript topic · the notebook
  name if the user gave one · what is needed back (which sources ground the claim and what they
  found). The agent resolves the notebook (asking the user when several candidates fit) and queries it.
- **Verification is mandatory.** NotebookLM is a *finding* layer, never a *verification*
  layer: resolve every paper in the agent's `Claims to verify` list through the PubMed tools (or DOI
  resolution) and confirm title/authors/year before proposing it. The prime directive is unchanged —
  no independently verified DOI/PMID, no citation.
- In the output template, write the `Source` field as
  `NotebookLM (<notebook name>) → PubMed-verified`.
- If the agent reports the MCP server unreachable or the session expired (it will suggest `nlm login`),
  skip this tier silently and fall through to Step 2.

## Step 2 — Consensus / PubMed (only if tiers 1–3 fail)

When the user's own material doesn't cover the claim, search externally. Prefer the
strongest available study design, in this order:

1. Systematic reviews & meta-analyses
2. Randomized controlled trials
3. Prospective observational studies
4. Retrospective studies

Use **landmark studies** when they remain the accepted standard, and prefer **recent**
evidence unless an older work is the canonical reference. Tools:
`mcp__claude_ai_Consensus__search` and the `mcp__claude_ai_PubMed__*` tools (search, get
metadata, convert IDs, lookup-by-citation) to retrieve and verify DOI/PMID. See
`references/research-r-consensus.md` for the study-type hierarchy, evidence-level labels, recency
vs. landmark guidance, and the mandatory Consensus MCP citation-format requirement.

**If those MCP connectors aren't authorized** (they need claude.ai OAuth and are unavailable in
non-interactive sessions), don't stop and never fabricate — fall back to the bundled
`scripts/pubmed_eutils.py`, which queries the public NCBI E-utilities API with **no auth**:

```
PLUGIN="${CLAUDE_PLUGIN_ROOT:-$(pwd)}"
python "$PLUGIN/skills/research/scripts/pubmed_eutils.py" --query "clear question / keywords" --retmax 5
python "$PLUGIN/skills/research/scripts/pubmed_eutils.py" --pmid 34567890            # verify one record
python "$PLUGIN/skills/research/scripts/pubmed_eutils.py" --doi 10.1001/jama.2019.4783   # resolve a DOI
```

It returns real records with DOI/PMID. See `references/research-r-consensus.md` → "No-auth
fallback" for limits (PubMed-only; no free Consensus equivalent) and when to ask the user to
authorize the connector.

## Citation quality bar

For every proposed reference:
- Return **complete bibliographic information**.
- Include **DOI** whenever available.
- Include **PMID** when available.
- Explain in **one or two sentences** why it supports the statement.
- Recommend **1–5 references** depending on the strength of evidence — a single strong
  meta-analysis may be enough; a contested claim may warrant several.

## Writing rules

- **Never modify citations the user already inserted.** Leave their existing references intact.
- **Never duplicate equivalent references** — same DOI or PMID means it's already there. Prefer the
  final published version over a preprint / early-access; don't list both.
- **Never cite papers that don't directly support the statement.** Tangential relevance is not support.
- **If evidence is conflicting, state that clearly** — present both sides rather than cherry-picking.
- **Preserve the writing style** of the manuscript.
- **Citation/bibliography FORMATTING is not this skill's job.** Creating/updating the in-text citations and
  the bibliography list inside a docx, and their style, belong to the **`zotero`** skill alone. Supply
  the real source's bibliographic record (title, authors, year, journal, DOI, PMID) + the evidence;
  `zotero` does the formatting. Canonical format definition:
  `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/zotero/references/zotero-r-citation-format.md`; the grammar of the
  `{{zref:ITEMKEY}}` marker placed in the text:
  `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/zotero/references/zotero-r-zref-protocol.md`.

## Report provenance (required)

Start every presented report/output with this provenance block, right under the title. List only
what was **actually** used this run (subagents and reference files); unused field = `—`:

```
Skill: research
Subagent: <called: journal-s-notebooklm / —>
References: <used: research-r-pdf.md / research-r-consensus.md / research-r-kunye.md>
---
```

## Output format

Present recommendations using the exact template in `references/research-r-kunye.md`. Begin the
output with the künye block above. Per
recommendation, always provide: Supported sentence · Recommended reference(s) · Why this
reference was selected · Evidence level · Source (User-provided reference / Uploaded PDF /
NotebookLM notebook / Consensus) · Page number (if PDF) · DOI · PMID (if available). That file also gives the
"no reliable evidence found" and "conflicting evidence" output variants.

## Reference files

- `references/research-r-pdf.md` — the fixed `pdflerim/` library, finding/searching uploaded PDFs, passage extraction, writer collaboration.
- `references/research-r-consensus.md` — Consensus/PubMed usage, study hierarchy, evidence levels.
- `references/research-r-kunye.md` — the mandatory output template + examples.
