<!-- Oluşturma: 20260725 0056 -->
# zotero — skill README

The plugin's single authority on Zotero. It runs in **two modes**:

- **Operation** — reference manager wired to the user's **real, local Zotero** installation. Mimics
  Zotero's own workflow: list library/collections, add sources by identifier, write in-text
  citations and the bibliography into Word, renumber on style change, pin citations.
- **Teaching** — when the user wants to do it *themselves* in the Zotero application, the browser or
  Word, the skill hands the question to the `zotero-s-teacher` agent, which answers from course
  notes distilled out of six video transcripts.

## When it triggers

**Operation** (from the SKILL.md `description`): *"zotero"*, *"kütüphaneme ekle"*,
*"kütüphanemde ne var"*, *"referans ekle"*, *"kaynakça oluştur"*, *"atıf ekle"*, *"DOI ile ekle"*,
*"PMID ile ekle"*, *"Word'e kaynakça bas"*, *"atıf stilini değiştir"*, *"dermelerimi listele"*.

**Teaching:** *"Zotero nasıl kullanılır"*, *"ISBN ile kitap ekle"*, *"sihirli değnek"*,
*"Connector kurulumu"*, *"senkronizasyon"*, *"Isnat 2 stili"*, *"DİA maddesi"*, *"Şamile"*,
*"Arapça isim nasıl yazılır"*, *"cilt sayfa nasıl verilir"*, *"mükerrer kayıtları birleştir"*,
*"Word'de Zotero sekmesi yok"*, *"düzeltmem kayboluyor"*, *"Unlink ne yapar"*.

## Input / output

- **Input:** a `.docx` carrying `{{zref:ITEMKEY}}` markers, and/or a DOI/PMID/ISBN/arXiv id, and/or a
  target citation style.
- **Output:** the docx with real in-text citations + an auto-generated bibliography. Default
  `--mode field` writes genuine Zotero field codes (`ADDIN ZOTERO_ITEM CSL_CITATION`), so the user's
  own Zotero + Word can Refresh and change the style afterwards. Operation summaries open with the
  mandatory provenance block.

## Subagents

**`zotero-s-teacher` — teaching mode only.** Red · `model: inherit` ·
`tools: Read, Glob, Grep, mcp__notebooklm-mcp__notebook_list, mcp__notebooklm-mcp__notebook_query`.
It has **no** `Write`/`Edit`/`Bash`, so it can neither touch a file nor run this skill's scripts —
the single-ownership rule holds at tool level. It answers from the six teaching references below,
states the Zotero version behind every step, refuses to sound certain about the ⚠️ items the videos
left unclear, and **makes the user take a backup before any operation that can lose data**
(bulk delete, emptying the trash, merging duplicates, resetting sync, Unlink Citations). When its
knowledge base has a gap and the NotebookLM MCP is connected, it queries the `zotero` notebook
before answering and cites what came back.

In **operation** mode the skill calls no agent; it works through its own scripts.

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

- `SKILL.md` — mode selection, connection layer, Zotero concept mapping, Word flow.

**Operation references**

- `references/zotero-r-zref-protocol.md` — `{{zref:ITEMKEY}}` marker grammar (the writer↔zotero contract).
- `references/zotero-r-citation-format.md` — in-text + bibliography format (Vancouver base), de-duplication.
- `references/zotero-r-add-methods.md` — the 5 add methods + writing to the library.
- `references/zotero-r-styles.md` — style resolution order (local CSL → Style Repository).
- `references/zotero-r-storage-bridge.md` — Zotero `storage/` PDFs as tier-2 evidence for research/writer.

**Teaching references** (read by `zotero-s-teacher`, Turkish — the UI labels are quoted verbatim
from the sources)

- `references/zotero-r-kaynak-ekleme.md` — the 4 add channels + AI→BibTeX bulk import + RDF.
- `references/zotero-r-atif-stilleri.md` — Word/Google Docs flow, ⚔️ Zotero 6/7/8, Isnat 2 install, Refresh, Unlink.
- `references/zotero-r-eklenti-senkron.md` — install, Connector, sync, 300 MB quota, 🔴 backup procedure.
- `references/zotero-r-ilahiyat.md` — DİA, Şamile, İSAM, Arabic names, multivolume works, Isnat 2 thesis fields.
- `references/zotero-r-organizasyon.md` — collections, tags, duplicates, notes and attachments.
- `references/zotero-r-tuzaklar.md` — pitfalls + the ⚠️ uncertainty inventory.
