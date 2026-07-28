# pdflerim — personal PDF library

Drop your own article PDFs **here**.

The `journalresearch` skill **always** scans this folder automatically during writing (when journalwriter asks for a
source for a claim):

```
PLUGIN="${CLAUDE_PLUGIN_ROOT:-$(pwd)}"
python "$PLUGIN/skills/journalresearch/scripts/journalresearch_pdfara.py" --dir "$PLUGIN/skills/journalresearch/pdflerim" --terms "keyword" "concept" ...
```

Matching pages are verified with the Read tool and proposed as a citation with a real DOI/PMID. Never a
fabricated citation — only evidence actually found in these PDFs or in verified sources is used.

- If the folder is empty, journalresearch silently switches to the general workspace/PubMed search.
- For PDF text extraction, `pip install pypdf` (if absent, journalresearch reads the PDFs directly with Read).

Detail: `../references/journalresearch-r-pdf.md` (step 0).
