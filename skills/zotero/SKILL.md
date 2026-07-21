---
name: zotero
description: >-
  Kullanıcının bilgisayarındaki GERÇEK Zotero kütüphanesine bağlanan referans
  yöneticisi. Zotero'nun iş akışını taklit eder: kütüphaneyi/dermeleri listeler,
  kimlik (DOI/PMID/ISBN/arXiv) ile kaynak ekler, Word (.docx) içine metin-içi
  atıf ve otomatik kaynakça basar, stil değişince yeniden numaralar (Refresh),
  atıfları sabitler (Unlink). Tetikleyiciler: "zotero", "kütüphaneme ekle",
  "kütüphanemde ne var", "referans ekle", "kaynakça oluştur", "atıf ekle",
  "DOI ile ekle", "PMID ile ekle", "Word'e kaynakça bas", "atıf stilini
  değiştir", "dermelerimi listele", "Zotero'daki makalelerim". Kullanıcı
  Zotero'daki kaynaklarına dayalı herhangi bir atıf/kaynakça işi istediğinde
  bu skili kullan. Keywords: Zotero, reference manager, kaynakça, atıf,
  bibliography, citation, collection, derme, DOI, PMID, RIS, BibTeX.
---

# zotero — Reference manager connected to the real Zotero

You connect to the user's installed Zotero (data directory: `$ZOTERO_DATA_DIR`,
or `~/Zotero` if unset). You do what Zotero does: collecting, organizing, citing.

## Single-ownership rule — the docx bibliography is only here

**Adding, removing, updating in-text citations and the bibliography list within a `.docx`, and the
style conversion, are ONLY this skill's authority.** No other
skill/agent (writer, journalstyle, research) touches the bibliography; they find/verify the source
(research), write the text (writer, writes the `{{zref:KEY}}` marker),
apply mechanical format (journalstyle) — and hand off the citation/bibliography mechanics to this skill.
Canonical format definition: `references/citation-format.md`.

## Core rule — inherited from research

**Do not fabricate any reference metadata.** Every record comes either from the user's real Zotero item
or from a verified DOI/PMID (via PubMed MCP / the `research` skill).
A source that cannot be verified is not added; in that case it is stated clearly.

## Connection layer

```
python scripts/zotero_lib.py --status              # backend status
python scripts/zotero_lib.py --list-collections    # collections
python scripts/zotero_lib.py --items [--collection "tez c2"] [--limit N]
python scripts/zotero_lib.py --get ITEMKEY
python scripts/zotero_lib.py --search "term"
```

- **sqlite (primary):** `zotero.sqlite` is copied and read — it **works even when Zotero is closed**.
  The output is CSL-JSON-like; the `attachments` field gives the real
  `storage\` PDF paths.
- **Live local API (secondary):** `http://127.0.0.1:23119` when Zotero 7 is open.
  **Writing** to the library (adding a new record) is done only this way — see
  `references/add-methods.md`. Never write directly to sqlite (it corrupts the library).
- Zotero closed + a write was requested → prepare the record, tell the user "open Zotero",
  send it once it is open.

## Zotero concept mapping

| Zotero | This skill |
|---|---|
| Collections | `--list-collections`, `--collection` filter |
| Add by Identifier | `references/add-methods.md` method 1 (DOI/PMID/ISBN/arXiv) |
| PDF drag-drop | method 3 (metadata extraction + PubMed verification) |
| .ris/.bib import | method 5 |
| Add/Edit Citation | `zotero_cite.py` marker: `{{zref:ITEMKEY}}` or `[@ITEMKEY]` |
| Add/Edit Bibliography | `zotero_cite.py --action refresh` (writes "Kaynaklar" at the end) |
| Refresh (smart text) | every `refresh` call renumbers + updates the bibliography |
| Unlink Citations | `--action unlink` (do not suggest unless the journal asks — no way back) |
| Style Repository | `references/styles.md` (local CSL → Style Repository; zotero applies the format) |

## Word flow (Add/Edit Citation + Bibliography)

1. Place/have placed markers at the citation points in the user's text:
   `{{zref:ITEMKEY}}` — the key is found with `zotero_lib.py --search`. The full grammar definition
   (grouped `{{zref:KEY1;KEY2}}`, the `[@ITEMKEY]` alias, missing-key behavior):
   `references/zref-protocol.md`.
2. Run:
   ```
   python scripts/zotero_cite.py --docx makale.docx [--style vancouver|author-date]
                                 [--mode field|text] [--out cikti.docx]
                                 [--heading "References"] [--no-red]
   ```
   - In a numbered style, `[1]`, `[2]`… by order of appearance; in an author-year style,
     `(Author, Year)`; the bibliography is automatic.
   - **`--mode field` (default): the output is a REAL Zotero field code**
     (`ADDIN ZOTERO_ITEM CSL_CITATION` + `ZOTERO_PREF` + `ZOTERO_BIBL`).
     The user's Zotero application **recognizes** these citations: in Word, the Zotero
     tab → Refresh renumbers, the style can be changed with Document Preferences
     (verified in the user's Zotero 7 + Word setup). A repeated
     script call only turns NEW markers into fields; it never touches existing
     `ZOTERO_*` fields — their owner is now Zotero.
   - **`--mode text`**: the old static-text behavior. A repeated call =
     Refresh: renumbers, rewrites the bibliography (idempotent —
     the markers stay in the document). The Zotero application does not see these citations;
     updating is only through this skill.
   - When an **existing** docx is updated, the added text is **red** (global rule);
     `--no-red` in a document produced from scratch.
3. Journal-specific fine style → the `references/styles.md` flow (local CSL → Style
   Repository); **this skill** applies the format, do not hand off to another agent/skill.
   In field mode, the user can also change the style directly from the Zotero application.
4. Before delivery (if the journal asks), pin: in field mode, Zotero's own
   **Unlink Citations** button; in text mode, `--action unlink`.

## Evidence bridge

The PDFs in the user's Zotero `storage\` folder are a tier-2 evidence source for
`research`/`writer` — see `references/storage-bridge.md`.

## Report provenance (required)

Every report/operation summary presented to the user starts, right under the title, with this provenance block; it lists the
references **actually** read in that job (no subagent → `—`; unused → `—`):

```
Skill: zotero
Subagent: —
References: <the ones read: add-methods.md / styles.md / storage-bridge.md / citation-format.md>
---
```

## Reference files

- `references/zref-protocol.md` — the `{{zref:ITEMKEY}}` marker grammar (the writer↔zotero handoff contract).
- `references/citation-format.md` — in-text citation + bibliography format (Vancouver base), de-duplication.
- `references/add-methods.md` — 5 add methods + writing to the library (saveItems).
- `references/styles.md` — Vancouver base, the resolution order for journal-specific styles.
- `references/storage-bridge.md` — including storage PDFs in the evidence search.
