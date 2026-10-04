<!-- Oluşturma: 20260725 2320 -->
# Word flow — Add/Edit Citation + Bibliography (the `journal-s-zotero` operation)

The full mechanics of turning `{{zref:…}}` markers in a `.docx` into real citations. Split out of
the agent body so it is loaded only when a docx is actually being rendered.

## The run

```
python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/zotero_docxatifbas.py" \
       --docx makale.docx [--style vancouver|author-date]
       [--mode field|text] [--out cikti.docx]
       [--heading "References"] [--no-red] [--color 0070C0] [--allow-mixed]
       [--allow-field-warnings]
```

0. **Engine inventory first — the script does it and refuses a mixed document.** A docx that has
   been through another reference manager can still carry its citation fields (`ADDIN EN.CITE`,
   `CITAVI`, Mendeley `CSL_CITATION`) beside the Zotero ones; their numbers follow that tool's
   sequence and match nothing in the Zotero bibliography. The script counts them per engine before
   reading the library and, by default, prints `{"error":"mixed_citation_engines","foreign_fields":
   {engine: {count, paragraphs}}}` and saves nothing. Convert or remove those fields first;
   `--allow-mixed` renders anyway and reports them as `foreign_citation_fields`. "How many citation
   fields does the docx have" is always answered per engine.
1. Markers must already sit at the citation points: `{{zref:ITEMKEY}}` (grouped:
   `{{zref:KEY1;KEY2}}`, alias `[@ITEMKEY]`). Keys come from `zotero_kutuphaneoku.py --search`.
   Grammar definition: `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-zref-protocol.md`.
2. Run the command above.
3. Journal-specific fine style → the `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-styles.md` flow (local CSL → Style
   Repository). **This agent** applies the format; it is handed to no one else. In field mode the
   user can also change the style straight from the Zotero application.
4. Before delivery (only if the journal asks), pin the citations: in field mode Zotero's own
   **Unlink Citations** button; in text mode `--action unlink`.

## Guarantees the caller relies on

- **The source file is never overwritten by default.** Without `--out` the result goes to
  `<ad>_zref.docx` beside it; in a plugin workspace the agent passes `--out` from the plugin-root
  resolver `scripts/cikti_yolcoz.py` (`<outputs_dir>/docx/<ad>_zref <stamp>.docx`, 1.22.0 layout —
  the script creates the `docx/` subfolder). The JSON report gives that path as `output` — **carry
  it to the next step**. An explicit `--out` aimed back at the source takes a `.bak` copy first
  (reported as `backup`).
- **Inline formatting survives.** Only the run holding the marker is split, so italics (*in vitro*,
  gene/species names), bold, super/subscript, hyperlinks and existing `ZOTERO_*` fields stay as
  they were.
- **Numbering follows true document order** — body paragraphs and table cells interleaved, so a
  citation inside a table in the middle of the manuscript gets the number its position deserves.
- **An unresolved key is never faked.** The marker is left in place (no `[?]` is written) and the
  key is reported in `unknown_keys`.
- Exactly **one** JSON object reaches stdout per run, whatever happens.

## Modes

**`--mode field` (default) — real Zotero field codes.** Output carries
`ADDIN ZOTERO_ITEM CSL_CITATION` + `ZOTERO_PREF` + `ZOTERO_BIBL`. The user's Zotero application
**recognizes** these: in Word the Zotero tab → Refresh renumbers, Document Preferences changes the
style (verified against the user's Zotero 7 + Word). A repeated script call only converts NEW
markers; existing `ZOTERO_*` fields belong to the Zotero app and are never touched. The preferences
field is prepended into the document's first paragraph, so no blank line appears at the top.

**`--mode text` — legacy static text.** A repeated call acts as Refresh: renumbers and rewrites the
bibliography, idempotent, markers stay in the document. The Zotero application does not see these
citations; only this agent can update them.

## Styles

- `--style vancouver` (default): numeric `[1]`, bibliography in citation order. Field-mode CSL id
  `http://www.zotero.org/styles/vancouver`.
- `--style author-date`: `(Author, Year)`, bibliography alphabetical. Field-mode CSL id
  `http://www.zotero.org/styles/apa`.

Anything beyond these two is handled here as well (read the CSL rules, apply) — or, in field mode,
from the Zotero app's Document Preferences.

## Verification in Word (1.19.0)

The script's JSON is a claim about the bytes it wrote; the outcome is what Word shows. With
Microsoft Word installed, `journal-s-zotero` runs
`python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/office_kopru.py" fields "<render>.docx"` after every
render: Word opens the file invisibly and read-only and the JSON returns `repair_prompt`,
`addin_total`, `zotero: {ZOTERO_ITEM, ZOTERO_BIBL, ZOTERO_TEMP}` and `zotero_pref_property`. The
agent compares `ZOTERO_ITEM` with `processed_markers` and reports `word_check` with `match: true |
false`. `--update --out "<outputs_dir>/docx/<stem>_zref_updated <stamp>.docx"` (resolved, not
composed) makes Word refresh the fields into a new file —
only on the user's ask; the render is never rewritten in place. Exit 2 `no_office` → `word_check:
skipped (no_office)`; a `modal_detected` result names a PNG of the dialog Word raised.

## A document that already carries Zotero fields

Since 1.29.0 the field-mode render reads the document it writes into (C2 thesis, 27 Sep 2026: 13
citations into 77 fields had to be done by hand before this; observation #357):
- **Pre-check before any write.** Fields whose visible result holds more than the citation
  (sentence text a Refresh would delete) and fields with `"dontUpdate": true` stop the run:
  `{"error":"existing_field_warnings","field_warnings":[{field, type, citation, result}]}`, nothing
  saved. Move the text out of the field / unfreeze it, or pass `--allow-field-warnings` knowingly;
  the warnings are then reported in the success JSON as `field_warnings`.
- **The document's style wins.** A numeric citation takes the bracket pair the existing fields
  print (`(n)` vs `[n]`, reported as `citation_wrap`); the `ZOTERO_PREF` style id is reported as
  `document_style`.
- **Existing items are cloned.** A new citation for a key the document already cites copies that
  field's `citationItems` (reported in `reused_items`), so both fields carry identical item data.
- **Colour.** `--color <hex>` sets the insert colour (e.g. `0070C0` for a blue revision round);
  default FF0000, reported as `insert_color`.
- **Renumbering is the user's Refresh.** New numbers are provisional, and no bibliography is
  written when a `ZOTERO_BIBL` exists; the JSON says `refresh_required: true` and the report tells the
  user Word → Zotero → Refresh. Edits to existing fields (`field` / `relink` / `delfield`) remain
  `skills/journalwriter/scripts/journalwriter_docxisaretliduzelt.py` ops inside journalwriter's
  marked-edit run.
- **After the Refresh**, read back: `dontUpdate` count (a hand-edited field keeps its stale number),
  and every printed number against its bibliography entry.

## Red-revision rule (global)

Updating an **existing** document colours every inserted run red (RGB 255,0,0). Pass `--no-red`
only for a brand-new document built from scratch.

## Zotero concept mapping

| Zotero button | Here |
|---|---|
| Add/Edit Citation | `{{zref:ITEMKEY}}` marker + `zotero_docxatifbas.py` |
| Add/Edit Bibliography | `--action refresh` (writes "Kaynaklar" at the end) |
| Refresh (smart text) | every `refresh` call renumbers + updates the bibliography |
| Unlink Citations | `--action unlink --mode text`. In `--mode field` the script refuses, points at Zotero's own button, prints one JSON and saves nothing |
| Style Repository | `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-styles.md` |
