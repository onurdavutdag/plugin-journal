# Output format

**Report provenance header (required):** The whole output starts with the skill provenance block —
before any recommendation — right under the title:

```
Skill: journalresearch
Subagent: <called: journal-s-notebooklm / —>
References: <the ones actually read in this work, e.g. journalresearch-r-pdf.md, journalresearch-r-consensus.md>
---
```

`Subagent:` names what was **actually** called this run — write `journal-s-notebooklm` whenever the
tier-3 notebook search ran, `—` when it did not. It is never left hardcoded; the block is how the
user audits which layer produced the evidence.

For **every** recommendation, produce one block with these fields in this order. Omit a field
only when the label says it is conditional (Page number, PMID).

**Note:** journalresearch gives the source's **metadata** (in a readable form so the user can audit it);
the **citation/bibliography formatting and list** that goes into the docx **belongs to the `journal-s-zotero` agent.** The
metadata below is shown in Vancouver layout, but this is not a "bibliography production", it is the source's
identity — the final format is applied by `journal-s-zotero`.

```
**Supported sentence:** <the exact sentence(s) from the manuscript this reference backs>
**Recommended reference(s):** <metadata (title·authors·year·journal·volume/issue/pages), 1–5 items>
**Why this reference was selected:** <1–2 sentences on how it supports the sentence>
**Evidence level:** <Level 1 SR/MA | Level 2 RCT | Level 3 prospective | Level 4 retrospective | Level 5 mechanistic/expert | Landmark>
**Source:** <User-provided reference | Uploaded PDF | NotebookLM (<notebook name>) → PubMed-verified | Consensus/PubMed>
**Page number (if PDF):** <page + section heading, or omit if not a PDF>
**DOI:** <doi, or "not available">
**PMID (if available):** <pmid, or omit>
```

When several sentences each need support, give one block per sentence. When one sentence is
supported by multiple references (strong evidence), list them under a single block.

## Filled example

```
**Supported sentence:** "Perioperative dexmedetomidine reduces the incidence of postoperative
delirium in elderly surgical patients."
**Recommended reference(s):**
1. Su X, Meng ZT, Wu XH, Cui F, Li HL, Wang DX, et al. Dexmedetomidine for prevention of delirium
   in elderly patients after non-cardiac surgery: a randomised, double-blind, placebo-controlled
   trial. Lancet. 2016;388(10054):1893-1902. doi:10.1016/S0140-6736(16)30580-3. PMID: 27542303.
2. Duan X, Coburn M, Rossaint R, Sanders RD, Waesberghe JV, Kowark A. Efficacy of perioperative
   dexmedetomidine on postoperative delirium: systematic review and meta-analysis. Br J Anaesth.
   2018;121(2):384-397. doi:10.1016/j.bja.2018.04.046. PMID: 30032879.
**Why this reference was selected:** The RCT [1] directly shows a lower delirium incidence with
dexmedetomidine in elderly postoperative patients; the meta-analysis [2] confirms the effect
across trials, giving Level 1 support.
**Evidence level:** Level 1 (meta-analysis) + Level 2 (RCT)
**Source:** Consensus
**Page number (if PDF):** —
**DOI:** 10.1016/S0140-6736(16)30580-3 ; 10.1016/j.bja.2018.04.046
**PMID (if available):** 27542303 ; 30032879
```

## Filled example — tier 3 (NotebookLM)

The notebook **found** the paper; PubMed **verified** it. Both halves go in the `Source` line, and
the provenance block's `Subagent:` names the agent that did the finding — otherwise the report
cannot show which layer the evidence came from.

```
Skill: journalresearch
Subagent: journal-s-notebooklm
References: journalresearch-r-kunye.md
---

**Supported sentence:** "Intraoperative hypotension is associated with postoperative acute kidney
injury in non-cardiac surgery."
**Recommended reference(s):**
1. Salmasi V, Maheshwari K, Yang D, Mascha EJ, Singh A, Sessler DI, et al. Relationship between
   intraoperative hypotension, defined by either reduction from baseline or absolute thresholds,
   and acute kidney and myocardial injury after noncardiac surgery. Anesthesiology.
   2017;126(1):47-65. doi:10.1097/ALN.0000000000001432. PMID: 27792044.
**Why this reference was selected:** The notebook surfaced it as the cohort that quantifies the
MAP thresholds; the association it reports is exactly the claim's content.
**Evidence level:** Level 3 (prospective cohort)
**Source:** NotebookLM (Anestezi Perioperatif) → PubMed-verified
**Page number (if PDF):** —
**DOI:** 10.1097/ALN.0000000000001432
**PMID (if available):** 27792044
```

A study the notebook surfaced but PubMed could **not** confirm is not written in this format at
all — it stays out of the report, as the prime directive requires.

## Variant — no reliable evidence found

State it plainly; do not fabricate to fill the gap.

```
**Supported sentence:** "<the claim>"
**Finding:** No reliable supporting evidence located in your provided references, your uploaded
PDFs, or Consensus/PubMed. Consider rewording the claim, softening it, or providing a source you
have in mind.
```

## Variant — conflicting evidence

Present both sides; let the author decide.

```
**Supported sentence:** "<the claim>"
**Finding — evidence is conflicting:**
- Supporting: <citation> — <one line>.
- Contradicting: <citation> — <one line>.
**Recommendation:** Reflect the uncertainty in the text (e.g., "evidence is mixed") and cite both.
```
