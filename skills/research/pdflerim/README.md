# pdflerim — personal PDF library

Drop your own article PDFs **here**.

The `research` skill **always** scans this folder automatically during writing (when writer asks for a
source for a claim):

```
python ../scripts/search_pdfs.py --dir . --terms "keyword" "concept" ...
```

Matching pages are verified with the Read tool and proposed as a citation with a real DOI/PMID. Never a
fabricated citation — only evidence actually found in these PDFs or in verified sources is used.

- If the folder is empty, research silently switches to the general workspace/PubMed search.
- For PDF text extraction, `pip install pypdf` (if absent, research reads the PDFs directly with Read).

Detail: `../references/research-r-pdf.md` (step 0).
