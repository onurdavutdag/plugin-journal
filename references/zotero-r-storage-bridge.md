# Evidence bridge — Zotero storage PDFs for journalresearch/journalwriter

The attached PDFs in the user's real Zotero library
(`<ZOTERO_DATA_DIR>/storage/<KEY>/*.pdf`) are a tier-2 evidence source — the same priority
as the journalresearch skill's "Uploaded PDF" tier.

## Flow

1. When `journalresearch` (or via journalwriter) searches for evidence for a claim, scan the Zotero storage too,
   **in addition to** the `pdflerim/` and workspace scan:

   ```
   python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalresearch/scripts/search_pdfs.py" --dir "C:/Users/onurd/Zotero/storage" --terms "concept" "keyword"
   ```

2. Find which Zotero item the hit PDF belongs to: the
   `storage/<ATTACHMENT_KEY>/` folder name in the file path is the attachment key; for the actual metadata,

   ```
   python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/zotero_lib.py" --items
   ```

   match against the `attachments` field in the output (exact path match). The matched
   item's `key, title, DOI, PMID` fields are ready metadata — **no fabrication,
   the metadata comes from the user's own library.**

3. Verify the hit per the journalresearch rule: open the PDF with Read at that page,
   confirm the passage actually supports the claim (a keyword coincidence is not
   support). The page number + section heading are reported.

4. In the output, use `Source: Uploaded PDF`; state the "Zotero library"
   sub-source in the rationale. The DOI/PMID comes from the item record; if missing, recovered with PubMed
   `lookup_article_by_citation`.

5. Writing the citation: since the item is already in the library, on the Word side the
   `{{zref:ITEMKEY}}` marker can be used directly — integrated with the journalwriter flow.

## Note

- The storage folder may have hundreds of PDFs; keep `--terms` specific, and if needed
  first narrow the candidate items with `zotero_lib.py --search`, then scan only those
  attachment paths.
- The PDFs of deleted (trashed) items may remain in storage; if you hit an attachment that
  does not appear in the `zotero_lib.py` output, do not use it without metadata.
