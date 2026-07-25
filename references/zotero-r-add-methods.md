# Adding a source — Zotero's 5 methods

All arrive at the same result: a **verified** CSL record. Never fabricated metadata —
every field comes either from the source itself or from PubMed/CrossRef verification.

## 1. By identifier (Add by Identifier) — DOI / PMID / ISBN / arXiv

- **PMID** → fetch the metadata with `mcp__claude_ai_PubMed__get_article_metadata`.
- **DOI** → convert to a PMID with `mcp__claude_ai_PubMed__convert_article_ids`,
  then fetch metadata; if not in PubMed, resolve the DOI via `https://doi.org/<doi>` with
  WebFetch (returns CrossRef content).
- **ISBN** (book) → publisher/WorldCat metadata via WebSearch; if unsure, have the
  user confirm the fields.
- **arXiv** → metadata from the `https://arxiv.org/abs/<id>` page.

## 2. Database / browser output

The user pastes a PubMed/Scopus page or metadata text → parse →
call `mcp__claude_ai_PubMed__lookup_article_by_citation` with title+author+year
and verify the DOI/PMID.

## 3. From a PDF (drag-drop equivalent)

1. Open the PDF's first page with Read (or scan with `search_pdfs.py`) —
   title, authors, journal, DOI are usually on the first page/footer.
2. Missing DOI/PMID → recover with `lookup_article_by_citation` (title+author+year).
3. Leave unverifiable fields empty, notify the user.

## 4. Manual entry

The user provides the fields. Required minimum: title, author(s), year, source type.
For a journal article, **always** try to verify the DOI/PMID from PubMed.

## 5. Import (.ris / .bib)

- `.ris`: `TY`, `AU`, `TI`, `T2/JO`, `PY`, `VL`, `IS`, `SP-EP`, `DO` tags.
- `.bib`: `@article{...}` fields (`author`, `title`, `journal`, `year`,
  `volume`, `number`, `pages`, `doi`).
- Parse each record → de-duplication check (same DOI/PMID = same article,
  see `references/zotero-r-citation-format.md`) → verify.

## Writing to the real library — only the live API

When Zotero is **open** (`zotero_lib.py --status` → `live_api: true`):

```
POST http://127.0.0.1:23119/connector/saveItems
Content-Type: application/json

{"items": [{"itemType": "journalArticle", "title": "...",
            "creators": [{"firstName": "...", "lastName": "...", "creatorType": "author"}],
            "date": "2016", "publicationTitle": "...", "volume": "...",
            "issue": "...", "pages": "...", "DOI": "...",
            "extra": "PMID: 27542303"}],
 "uri": "http://localhost/claude-zotero-skill"}
```

- The PMID is written into the `extra` field as `PMID: <n>` (Zotero convention).
- Response 201 → the record landed in the user's library; confirm with `zotero_lib.py --search`.
- If Zotero is closed: prepare the record as JSON, show it to the user,
  say "I'll add it once you open Zotero". **Never write directly to sqlite.**
- Before adding, de-duplication: `zotero_lib.py --search "<doi or title>"` —
  if the same DOI/PMID exists, do not add, use the existing item's key.
