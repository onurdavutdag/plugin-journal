# Citation format — OWNER: journal-s-zotero

This is the **sole authoritative definition** of the in-text citation and bibliography format within a docx.
The skills (journalresearch/journalwriter/journalstyle) do not format citations/bibliography; they produce
metadata/evidence and hand off to this agent. `zotero_docxatifbas.py` applies these rules.

The default style is **Vancouver** (numbered, most biomedical journals). If the user/journal
wants a different style, go through the `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-styles.md` resolution order.

## Vancouver — bibliography list format

`Authors. Title. Journal Abbreviation. Year;Volume(Issue):Pages. doi:DOI. PMID: PMID.`

Rules:
- Authors as *Last name Initials*, comma-separated. If there are **more than 6 authors**, the first six + `et al.`
- The journal name is abbreviated (NLM/Index Medicus style).
- Add the **DOI** if present; add the **PMID** if present.

**Example (journal article, DOI + PMID):**

```
1. Su X, Meng ZT, Wu XH, Cui F, Li HL, Wang DX, et al. Dexmedetomidine for prevention of
   delirium in elderly patients after non-cardiac surgery: a randomised, double-blind,
   placebo-controlled trial. Lancet. 2016;388(10054):1893-1902.
   doi:10.1016/S0140-6736(16)30580-3. PMID: 27542303.
```

## Other styles (if requested)

- **AMA**: very close to Vancouver; in-text superscript number.
- **APA (7th)**: author–date, e.g. `Su, X., Meng, Z. T., ... (2016). Title. *Lancet*, 388(10054),
  1893–1902. https://doi.org/10.1016/S0140-6736(16)30580-3` — `zotero_docxatifbas.py --style author-date`.
- For a journal-specific numbered/author-year style, `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-styles.md` (local CSL → Style Repository).
- If the manuscript already uses a style, follow it; if the user's existing references reveal a style,
  do not impose the default.

## De-duplication

Before adding to the bibliography, check whether it already exists:
- **Same DOI or same PMID = same article** — never add twice.
- Watch for near-duplicates: preprint vs published version, early-access vs paginated final. Prefer the final
  published version, do not list both.
- Do not suggest a citation the user added themselves to that sentence; leave the existing citation as is.
