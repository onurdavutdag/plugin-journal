# Adding a source — Zotero's 5 methods

All arrive at the same result: a **verified** CSL record. Never fabricated metadata —
every field comes either from the source itself or from PubMed verification.

## How this agent verifies — one path only

`journal-s-zotero` carries **no MCP tool and no web tool** (`tools: ["Read", "Glob", "Grep",
"Bash"]`). Verification therefore runs through Bash, on the script the plugin already ships:

```
EU="${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalresearch/scripts/pubmed_eutils.py"
python "$EU" --pmid 27542303          # one or more PMIDs → full records
python "$EU" --doi 10.1001/jama.2019.4783
python "$EU" --query "title author year" --retmax 5
```

It reaches NCBI E-utilities, which needs **no authentication and no API key**, so the path holds
in a non-interactive session too. Output is JSON on stdout; `{"error": ...}` means NCBI was
unreachable — report that, do not invent the record.

What this path cannot resolve — an ISBN, an arXiv id, or a DOI absent from PubMed — is **not
guessed**. Ask the user for the fields (method 4), or return and let the caller run
`journalresearch`, which owns source finding and holds the web/MCP tools for it.

## 1. By identifier (Add by Identifier) — DOI / PMID / ISBN / arXiv

- **PMID** → `python "$EU" --pmid <n>`.
- **DOI** → `python "$EU" --doi <doi>`. Not in PubMed → the identifier stays unresolved here;
  ask the user or hand back to the caller. Do not reconstruct the record from the DOI string.
- **ISBN** (book) → outside this path. Take the fields from the user (method 4) and mark
  the record as user-supplied.
- **arXiv** → outside this path, same treatment as ISBN.

## 2. Database / browser output

The user pastes a PubMed/Scopus page or metadata text → parse title + first author + year →
`python "$EU" --query "<title> <author> <year>" --retmax 5` → match the returned record and
verify its DOI/PMID against what was pasted. No confident match → do not add.

## 3. From a PDF (drag-drop equivalent)

1. Open the PDF's first page with `Read` (or scan with
   `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalresearch/scripts/search_pdfs.py`) —
   title, authors, journal, DOI are usually on the first page/footer.
2. Missing DOI/PMID → recover with `python "$EU" --query "<title> <author> <year>"`.
3. Leave unverifiable fields empty, notify the user.

## 4. Manual entry

The user provides the fields. Required minimum: title, author(s), year, source type.
For a journal article, **always** try `--doi`/`--query` first; only fall back to the
user's own fields when the lookup returns nothing.

## 5. Import (.ris / .bib)

- `.ris`: `TY`, `AU`, `TI`, `T2/JO`, `PY`, `VL`, `IS`, `SP-EP`, `DO` tags.
- `.bib`: `@article{...}` fields (`author`, `title`, `journal`, `year`,
  `volume`, `number`, `pages`, `doi`).
- Parse each record → de-duplication check (same DOI/PMID = same article,
  see `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-citation-format.md`) → verify each `DO`/`doi` with
  `python "$EU" --doi <doi>`.

## Writing to the real library — `zotero_save.py`

Do not hand-roll the HTTP call. One script owns the write, so de-duplication, the
Zotero-is-closed case and the JSON body are handled the same way every time:

```
python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/zotero_save.py" --item '<json>'
python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/zotero_save.py" --from-file rec.json --dry-run
```

The item is a Zotero connector object:

```json
{"itemType": "journalArticle", "title": "...",
 "creators": [{"firstName": "...", "lastName": "...", "creatorType": "author"}],
 "date": "2016", "publicationTitle": "...", "volume": "...",
 "issue": "...", "pages": "...", "DOI": "...", "extra": "PMID: 27542303"}
```

- The PMID goes into `extra` as `PMID: <n>` (Zotero convention) — the script enforces this
  when a bare `PMID` key is passed instead.
- One run prints **exactly one JSON object**: `{"status", "itemkey", "duplicate_of",
  "prepared", "error"}`. Pass its fields through; do not paraphrase them.
- `status` values: `added` (201, key confirmed by a follow-up search) · `duplicate`
  (same DOI/PMID already in the library — `duplicate_of` carries the existing key, nothing
  was written) · `zotero_closed` (`prepared` carries the record; tell the user to open
  Zotero and hand the payload back to the caller) · `error`.
- `--dry-run` runs the de-duplication check and prints the payload without POSTing.
- Writes go through the live API only. **Never write directly to `zotero.sqlite`** — it
  corrupts the library; `zotero_lib.py` stays read-only by design.
