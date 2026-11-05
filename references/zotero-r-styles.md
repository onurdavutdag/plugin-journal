# Citation styles — resolution order (Style Repository logic)

The docx citation/bibliography format is **`journal-s-zotero`'s authority only.** The canonical format definition is the
sibling `zotero-r-citation-format.md` file in this same plugin-root `references/` folder. Default: **Vancouver**
(numbered; 6 authors + et al., NLM journal abbreviation, DOI+PMID). `zotero_docxatifbas.py --style vancouver` produces this
base; `--style author-date` produces an APA-like base. The skills do not do this job, they hand off to the agent.

## What a Word "Refresh" does to the rendered document (1.33.6, #832)

The render prints the citations itself, but the Zotero Word add-in re-renders every field from the style named in
the `ZOTERO_PREF_1` field the moment the user presses Refresh. So the preference, not the printed text, is the
delivered layout. Since 1.33.6 the `vancouver` base writes `http://www.zotero.org/styles/vancouver-brackets` (the
official "NLM/Vancouver: Citing Medicine 2nd edition (citation-sequence, brackets)" CSL), `locale="en-US"` and
`automaticJournalAbbreviations="false"`. Why (Chiari manuscript, 5 Nov 2026): the plain `vancouver` id turned every
"[1,2]" into "(1,2)", the bibliography terms came out in the document language ("vd." instead of "et al." — the
exact setting is unverified), the style appended "PubMed PMID: …" to every entry, and the automatic abbreviation
list printed "Glob Spine J" although the item field held "Global Spine J". The render report states which style id
the preference carries; if that CSL is not installed in the user's Zotero, the report hands over the one-line
install (`https://www.zotero.org/styles/vancouver-brackets`, double-click the downloaded `.csl`). A citation audit
before hand-over reads the preference field as well as the printed numbers. A wrong item field (year, abbreviation)
is not fixable through `zotero_kutuphaneyaz.py` (adds only; local-API PATCH answers 501) — use the Run-JavaScript
handoff in `zotero-r-add-methods.md`.

## When a journal-specific style is requested

When the user gives a target journal name ("in AJNR style", "for Spine"), in order:

1. **Local Zotero CSL repository:** search for the journal name in `~/Zotero/styles/*.csl`
   (Glob + Grep the `<title>` tag). The styles the user installed into their Zotero are
   here — if present, read their rules (numbered or author-year, `et-al-min`,
   punctuation) from the CSL XML.
2. **journalstyle profile:** if the journalstyle skill has cached a profile for that journal
   (`authorguidelines/<slug>.json`, the `citation_style` field), use it — the profile wins in a
   conflict (it is derived from the journal guidelines).
3. **Neither found — do not fetch from the web.** This agent carries no web tool
   (`tools: ["Read", "Glob", "Grep", "Bash"]`, see `zotero-r-add-methods.md`), so the Zotero Style
   Repository is out of reach. Tell the user the CSL is not installed locally and ask them to install
   it into Zotero (Zotero → Edit → Settings → Cite → Get additional styles, or
   `https://www.zotero.org/styles?q=<journal>` in a browser), then re-run step 1. Until then, fall
   back to the base style the profile or the user names (numbered → `vancouver`, author-year →
   `author-date`) and say in the report that the journal-specific fine rules were not applied.

## Application

- Base selection: if the style is numbered, produce/refresh the document with `zotero_docxatifbas.py --style vancouver`,
  if author-year, with `--style author-date`.
- Fine details (superscript number, square/parenthesis difference, et-al threshold,
  italics, the "References" heading name) are **zotero's own responsibility** —
  apply the rule read from the local CSL/Style Repository with `zotero_docxatifbas.py` parameters
  (`--heading`, style selection) and, if needed, a targeted correction on the output.
  Do not hand this job to another agent/skill; the authority stays in one hand.
- After a style change, always work on a document that has had `zotero_docxatifbas.py` refresh
  run — since the markers stay in the document, the style transition is
  lossless (the Vancouver ⇄ author-date transition has been tested).
- **Two ways to change the style** (no conflict):
  1. **From the Zotero application** — the live fields in the `--mode field` (default) output
     belong to Zotero: in Word, the Zotero tab → Document Preferences →
     select style → Refresh. All CSL styles (Style Repository) are available.
  2. **From this skill** — `zotero_docxatifbas.py --style ...` sets the base style when writing new
     markers; in text-mode documents this is the only way.

## De-duplication and language

- Same DOI/PMID = same article — it does not enter the bibliography a second time
  (`zotero-r-citation-format.md` rule).
- In a Turkish document output the bibliography heading is "Kaynaklar"; in an English document
  `--heading "References"`. The number/percentage format is subject to the global CLAUDE.md language rule.
