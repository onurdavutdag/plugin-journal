# Evidence bridge — Zotero storage PDFs for journalresearch/journalwriter

The attached PDFs in the user's real Zotero library
(`<ZOTERO_DATA_DIR>/storage/<KEY>/*.pdf`) are a tier-2 evidence source — the same priority
as the journalresearch skill's "Uploaded PDF" tier.

## Where the line falls

**Querying the library is `journal-s-zotero`'s job; reading a PDF that already sits on disk is
journalresearch's.** The skill never runs `zotero_lib.py` and never opens `zotero.sqlite`: it asks
the agent for the item records plus their attachment paths, then works on those paths with the
tools it already has. This keeps §7's single ownership intact — one component touches the library,
and the evidence tier still works.

## Flow

1. **Ask the agent for the candidate items.** Call `journal-s-zotero` with the `Task` tool, naming
   the collection (or the search term) and asking for the items with their `attachments` paths.
   It returns records carrying `key, title, DOI, PMID` and the real `storage/<KEY>/*.pdf` paths —
   **ready metadata, no fabrication, straight from the user's own library.**

2. **Scan only the returned paths** with the skill's own searcher — never the storage root:

   ```
   python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalresearch/scripts/search_pdfs.py" \
     --dir "<one returned storage/<KEY> folder>" --terms "concept" "keyword"
   ```

   This runs **in addition to** the `pdflerim/` and workspace scan, not instead of it.

3. Verify the hit per the journalresearch rule: open the PDF with Read at that page,
   confirm the passage actually supports the claim (a keyword coincidence is not
   support). The page number + section heading are reported.

4. In the output, use `Source: Uploaded PDF`; state the "Zotero library"
   sub-source in the rationale. The DOI/PMID comes from the item record the agent returned; if it
   is missing, recover it with PubMed `lookup_article_by_citation` or
   `skills/journalresearch/scripts/pubmed_eutils.py --query`.

5. Writing the citation: since the item is already in the library, on the Word side the
   `{{zref:ITEMKEY}}` marker can be used directly — integrated with the journalwriter flow.
   The marker is all the caller writes; the bibliography itself stays `journal-s-zotero`'s.

## Note

- The storage folder may hold hundreds of PDFs. Never hand the whole root to `--dir`; narrow the
  candidates through the agent first (collection or search term), then scan only those paths.
- The PDFs of deleted (trashed) items may remain in storage. An attachment path the agent did not
  return has no metadata behind it — do not use it.
- On the agent side this is the "evidence paths" job listed in `journal-s-zotero`'s
  "When to invoke"; it returns records and paths and does not read the PDFs itself.
