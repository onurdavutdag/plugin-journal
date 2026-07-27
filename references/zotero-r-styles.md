# Citation styles — resolution order (Style Repository logic)

The docx citation/bibliography format is **`journal-s-zotero`'s authority only.** The canonical format definition is the
sibling `zotero-r-citation-format.md` file in this same plugin-root `references/` folder. Default: **Vancouver**
(numbered; 6 authors + et al., NLM journal abbreviation, DOI+PMID). `zotero_cite.py --style vancouver` produces this
base; `--style author-date` produces an APA-like base. The skills do not do this job, they hand off to the agent.

## When a journal-specific style is requested

When the user gives a target journal name ("in AJNR style", "for Spine"), in order:

1. **Local Zotero CSL repository:** search for the journal name in `~/Zotero/styles/*.csl`
   (Glob + Grep the `<title>` tag). The styles the user installed into their Zotero are
   here — if present, read their rules (numbered or author-year, `et-al-min`,
   punctuation) from the CSL XML.
2. **Zotero Style Repository (web):** if not present, find the style via
   `https://www.zotero.org/styles?q=<journal>`; fetch the CSL file with
   WebFetch and extract the rules.
3. **journalstyle profile:** if the journalstyle skill has cached a profile for that journal
   (the `citation_style` field), use it — the profile wins in a conflict
   (it is derived from the journal guidelines).

## Application

- Base selection: if the style is numbered, produce/refresh the document with `zotero_cite.py --style vancouver`,
  if author-year, with `--style author-date`.
- Fine details (superscript number, square/parenthesis difference, et-al threshold,
  italics, the "References" heading name) are **zotero's own responsibility** —
  apply the rule read from the local CSL/Style Repository with `zotero_cite.py` parameters
  (`--heading`, style selection) and, if needed, a targeted correction on the output.
  Do not hand this job to another agent/skill; the authority stays in one hand.
- After a style change, always work on a document that has had `zotero_cite.py` refresh
  run — since the markers stay in the document, the style transition is
  lossless (the Vancouver ⇄ author-date transition has been tested).
- **Two ways to change the style** (no conflict):
  1. **From the Zotero application** — the live fields in the `--mode field` (default) output
     belong to Zotero: in Word, the Zotero tab → Document Preferences →
     select style → Refresh. All CSL styles (Style Repository) are available.
  2. **From this skill** — `zotero_cite.py --style ...` sets the base style when writing new
     markers; in text-mode documents this is the only way.

## De-duplication and language

- Same DOI/PMID = same article — it does not enter the bibliography a second time
  (`zotero-r-citation-format.md` rule).
- In a Turkish document output the bibliography heading is "Kaynaklar"; in an English document
  `--heading "References"`. The number/percentage format is subject to the global CLAUDE.md language rule.
