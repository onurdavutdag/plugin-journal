---
name: zotero
description: >-
  Bu skill Zotero konusunda tek mercidir; iki iş yapar. (1) OPERASYON — kullanıcının
  GERÇEK Zotero kütüphanesine bağlanır: dermeleri listeler, kimlik (DOI/PMID/ISBN/arXiv)
  ile kaynak ekler, Word (.docx) içine metin-içi atıf ve kaynakça basar, stil değişince
  yeniden numaralar (Refresh), atıfları sabitler (Unlink). Tetikleyiciler: "zotero",
  "kütüphaneme ekle", "referans ekle", "kaynakça oluştur", "atıf ekle", "DOI ile ekle",
  "Word'e kaynakça bas", "atıf stilini değiştir", "dermelerimi listele".
  (2) ÖĞRETİM — kullanıcı Zotero'yu KENDİ ELİYLE kullanmayı sorduğunda ders notlarına
  dayalı rehberlik eder (zotero-s-teacher alt-ajanı): "Zotero nasıl kullanılır",
  "ISBN ile kitap ekle", "sihirli değnek", "Connector kurulumu", "senkronizasyon",
  "Isnat 2 stili", "DİA maddesi", "Şamile", "Arapça isim nasıl yazılır", "cilt sayfa
  nasıl verilir", "mükerrer kayıtları birleştir", "düzeltmem kayboluyor".
  Keywords: Zotero, kaynakça, atıf, bibliography, citation, derme, DOI, BibTeX,
  Isnat, DİA, Şamile, Connector.
version: 1.6.1
---

# zotero — Reference manager connected to the real Zotero

Connect to the user's installed Zotero (data directory: `$ZOTERO_DATA_DIR`,
or `~/Zotero` if unset). Do what Zotero does: collecting, organizing, citing.

## Two modes — decide first

Read the request and pick one. They never mix in a single answer.

| The user wants… | Mode | What happens |
|---|---|---|
| A file processed — citations/bibliography written into a `.docx`, the library queried, a source added by DOI/PMID, a style renumbered | **Operation** | This SKILL.md's own flow: `zotero_lib.py` / `zotero_cite.py`. Continue below |
| To learn how to do it **themselves** in the Zotero application, the browser or Word — steps, menus, versions, rules, an error explained | **Teaching** | Delegate to the **`zotero-s-teacher`** agent (Task tool). Hand over the question plus the absolute path of `${CLAUDE_PLUGIN_ROOT}/skills/zotero/references/` |

Signals for teaching mode: *"nasıl"*, *"nereden"*, *"ne işe yarar"*, *"neden böyle oldu"*, a menu
or button name, a Zotero version, Isnat 2 / DİA / Şamile / Arapça isim / Connector /
senkronizasyon / mükerrer kayıt. The agent is read-only — it never touches a file and never runs a
script, so the single-ownership rule below stays intact.

## Single-ownership rule — the docx bibliography is only here

**Adding, removing, updating in-text citations and the bibliography list within a `.docx`, and the
style conversion, are ONLY this skill's authority.** No other
skill/agent (writer, journalstyle, research) touches the bibliography; they find/verify the source
(research), write the text (writer, writes the `{{zref:KEY}}` marker),
apply mechanical format (journalstyle) — and hand off the citation/bibliography mechanics to this skill.
Canonical format definition: `references/zotero-r-citation-format.md`.

## Core rule — inherited from research

**Do not fabricate any reference metadata.** Every record comes either from the user's real Zotero item
or from a verified DOI/PMID (via PubMed MCP / the `research` skill).
A source that cannot be verified is not added; in that case it is stated clearly.

## Connection layer

```
PLUGIN="${CLAUDE_PLUGIN_ROOT:-$(pwd)}"
python "$PLUGIN/skills/zotero/scripts/zotero_lib.py" --status              # backend status
python "$PLUGIN/skills/zotero/scripts/zotero_lib.py" --list-collections    # collections
python "$PLUGIN/skills/zotero/scripts/zotero_lib.py" --items [--collection "tez c2"] [--limit N]
python "$PLUGIN/skills/zotero/scripts/zotero_lib.py" --get ITEMKEY
python "$PLUGIN/skills/zotero/scripts/zotero_lib.py" --search "term"
```

(`${CLAUDE_PLUGIN_ROOT}` gives the plugin root; in a global install cwd is the workspace, so scripts
are called with this variable — a relative `scripts/...` path breaks globally.)

- **sqlite (primary):** `zotero.sqlite` is copied and read — it **works even when Zotero is closed**.
  The output is CSL-JSON-like; the `attachments` field gives the real
  `storage\` PDF paths.
- **Live local API (secondary):** `http://127.0.0.1:23119` when Zotero 7 is open.
  **Writing** to the library (adding a new record) is done only this way — see
  `references/zotero-r-add-methods.md`. Never write directly to sqlite (it corrupts the library).
- Zotero closed + a write was requested → prepare the record, tell the user "open Zotero",
  send it once it is open.

## Zotero concept mapping

| Zotero | This skill |
|---|---|
| Collections | `--list-collections`, `--collection` filter |
| Add by Identifier | `references/zotero-r-add-methods.md` method 1 (DOI/PMID/ISBN/arXiv) |
| PDF drag-drop | method 3 (metadata extraction + PubMed verification) |
| .ris/.bib import | method 5 |
| Add/Edit Citation | `zotero_cite.py` marker: `{{zref:ITEMKEY}}` or `[@ITEMKEY]` |
| Add/Edit Bibliography | `zotero_cite.py --action refresh` (writes "Kaynaklar" at the end) |
| Refresh (smart text) | every `refresh` call renumbers + updates the bibliography |
| Unlink Citations | `--action unlink --mode text` (do not suggest unless the journal asks — no way back). In `--mode field` the script refuses and points at Zotero's own button; it prints one JSON and saves nothing. |
| Style Repository | `references/zotero-r-styles.md` (local CSL → Style Repository; zotero applies the format) |

## Word flow (Add/Edit Citation + Bibliography)

1. Place/have placed markers at the citation points in the user's text:
   `{{zref:ITEMKEY}}` — the key is found with `zotero_lib.py --search`. The full grammar definition
   (grouped `{{zref:KEY1;KEY2}}`, the `[@ITEMKEY]` alias, missing-key behavior):
   `references/zotero-r-zref-protocol.md`.
2. Run:
   ```
   python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/zotero/scripts/zotero_cite.py" \
          --docx makale.docx [--style vancouver|author-date]
          [--mode field|text] [--out cikti.docx]
          [--heading "References"] [--no-red]
   ```
   - **The source file is never overwritten by default.** Without `--out` the result
     goes to `<ad>_zref.docx` beside it; pass that `output` path from the JSON report
     to the next step. An explicit `--out` aimed back at the source takes a `.bak`
     copy first (reported as `backup`).
   - Inline formatting survives: only the run holding the marker is split, so italics
     (*in vitro*, gene/species names), bold, super/subscript, hyperlinks and existing
     `ZOTERO_*` fields stay as they were.
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
3. Journal-specific fine style → the `references/zotero-r-styles.md` flow (local CSL → Style
   Repository); **this skill** applies the format, do not hand off to another agent/skill.
   In field mode, the user can also change the style directly from the Zotero application.
4. Before delivery (if the journal asks), pin: in field mode, Zotero's own
   **Unlink Citations** button; in text mode, `--action unlink`.

## Evidence bridge

The PDFs in the user's Zotero `storage\` folder are a tier-2 evidence source for
`research`/`writer` — see `references/zotero-r-storage-bridge.md`.

## Report provenance (required)

Every report/operation summary presented to the user starts, right under the title, with this provenance block; it lists the
references **actually** read in that job (no subagent → `—`; unused → `—`):

```
Skill: zotero
Subagent: — (teaching mode: zotero-s-teacher)
References: <the ones read: add-methods.md / styles.md / storage-bridge.md / citation-format.md>
---
```

## Reference files

**Operation mode** (this skill reads them):

- `references/zotero-r-zref-protocol.md` — the `{{zref:ITEMKEY}}` marker grammar (the writer↔zotero handoff contract).
- `references/zotero-r-citation-format.md` — in-text citation + bibliography format (Vancouver base), de-duplication.
- `references/zotero-r-add-methods.md` — 5 add methods + writing to the library (saveItems).
- `references/zotero-r-styles.md` — Vancouver base, the resolution order for journal-specific styles.
- `references/zotero-r-storage-bridge.md` — including storage PDFs in the evidence search.

**Teaching mode** (the `zotero-s-teacher` agent reads them; distilled from six video transcripts and
verified against the NotebookLM `zotero` notebook). Do not load these for an operation job:

- `references/zotero-r-kaynak-ekleme.md` — the 4 add channels (manual · magic wand · Connector · PDF drag), the AI→BibTeX bulk import, RDF import/export, the channel decision rule.
- `references/zotero-r-atif-stilleri.md` — the Word/Google Docs flow (Add/Edit Citation, prefix/suffix, Bibliography, Refresh, Unlink), the ⚔️ Zotero 6/7/8 differences, volume-page notation, Isnat 2 / APA / Chicago install and switching.
- `references/zotero-r-eklenti-senkron.md` — install, Connector pinning, account, the ⚔️ sync menu paths, the 300 MB quota and the 🔴 **backup procedure + the list of operations that require a backup first**.
- `references/zotero-r-ilahiyat.md` — DİA and Şamile group libraries, İSAM, the Arabic two-field harf-i tarif technique, multivolume works, the 🔴 Isnat 2 thesis fields.
- `references/zotero-r-organizasyon.md` — collections, tags, the two different delete actions, merging duplicates, notes and attachments.
- `references/zotero-r-tuzaklar.md` — the pitfalls (manual edits in Word, duplicate/ghost records, performance, Unlink) and the **⚠️ uncertainty inventory** of what the sources never made clear.
