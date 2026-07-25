<!-- Oluşturma: 20260725 0056 -->
# zotero — skill README

Reference manager wired to the user's **real, local Zotero** installation. Mimics Zotero's own
workflow: list library/collections, add sources by identifier, write in-text citations and the
bibliography into Word, renumber on style change, pin citations.

## When it triggers

Turkish trigger phrases (from the SKILL.md `description`): *"zotero"*, *"kütüphaneme ekle"*,
*"kütüphanemde ne var"*, *"referans ekle"*, *"kaynakça oluştur"*, *"atıf ekle"*, *"DOI ile ekle"*,
*"PMID ile ekle"*, *"Word'e kaynakça bas"*, *"atıf stilini değiştir"*, *"dermelerimi listele"*.

## Input / output

- **Input:** a `.docx` carrying `{{zref:ITEMKEY}}` markers, and/or a DOI/PMID/ISBN/arXiv id, and/or a
  target citation style.
- **Output:** the docx with real in-text citations + an auto-generated bibliography. Default
  `--mode field` writes genuine Zotero field codes (`ADDIN ZOTERO_ITEM CSL_CITATION`), so the user's
  own Zotero + Word can Refresh and change the style afterwards. Operation summaries open with the
  mandatory provenance block.

## Subagents

**None.** This skill calls no agents; it works through its own scripts.

- `scripts/zotero_lib.py` — read layer. `zotero.sqlite` is copied and read (**works with Zotero
  closed**); the live local API `127.0.0.1:23119` is the secondary backend.
- `scripts/zotero_cite.py` — the Word layer (cite / refresh / unlink). Writes `<ad>_zref.docx`
  by default (the source is never overwritten silently) and preserves inline formatting,
  hyperlinks and existing `ZOTERO_*` fields; use the `output` path from its JSON report.

## Constraints

- **Sole authority** for docx in-text citations and the bibliography — `writer`, `research` and
  `journalstyle` all hand this work over and never touch the bibliography themselves.
- No fabricated metadata: every record comes from a real Zotero item or a verified DOI/PMID.
- **Never writes to `zotero.sqlite` directly** (it corrupts the library) — writes go through the
  local API, which needs Zotero to be open.
- Updating an existing docx colors added text red (global rule); `--no-red` for a fresh document.

## Files

- `SKILL.md` — connection layer, Zotero concept mapping, Word flow.
- `references/zotero-r-zref-protocol.md` — `{{zref:ITEMKEY}}` marker grammar (the writer↔zotero contract).
- `references/zotero-r-citation-format.md` — in-text + bibliography format (Vancouver base), de-duplication.
- `references/zotero-r-add-methods.md` — the 5 add methods + writing to the library.
- `references/zotero-r-styles.md` — style resolution order (local CSL → Style Repository).
- `references/zotero-r-storage-bridge.md` — Zotero `storage/` PDFs as tier-2 evidence for research/writer.
