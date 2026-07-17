# Output format

**Report künye header (zorunlu):** The whole output starts with the skill provenance block —
before any recommendation — right under the title:

```
Skill: research
Subagent: —
References: <bu çalışmada fiilen okunanlar, ör. research-r-pdf.md, research-r-consensus.md>
---
```

For **every** recommendation, produce one block with these fields in this order. Omit a field
only when the label says it is conditional (Page number, PMID).

**Not:** research kaynağın **künyesini** verir (kullanıcı denetleyebilsin diye okunur biçimde);
docx'e girecek **atıf/kaynakça biçimlemesi ve listesi `zotero`'nundur.** Aşağıdaki künye Vancouver
düzeninde gösterilir ama bu bir "kaynakça üretimi" değil, kaynağın kimliğidir — nihai biçimi
`zotero` uygular.

```
**Supported sentence:** <the exact sentence(s) from the manuscript this reference backs>
**Recommended reference(s):** <künye (başlık·yazarlar·yıl·dergi·cilt/sayı/sayfa), 1–5 adet>
**Why this reference was selected:** <1–2 sentences on how it supports the sentence>
**Evidence level:** <Level 1 SR/MA | Level 2 RCT | Level 3 prospective | Level 4 retrospective | Level 5 mechanistic/expert | Landmark>
**Source:** <User-provided reference | Uploaded PDF | Consensus>
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
