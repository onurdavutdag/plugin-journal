<!-- Oluşturma: 20260725 2320 -->
# Word flow — Add/Edit Citation + Bibliography (the `journal-s-zotero` operation)

The full mechanics of turning `{{zref:…}}` markers in a `.docx` into real citations. Split out of
the agent body so it is loaded only when a docx is actually being rendered.

## The run

```
python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/scripts/zotero_cite.py" \
       --docx makale.docx [--style vancouver|author-date]
       [--mode field|text] [--out cikti.docx]
       [--heading "References"] [--no-red]
```

1. Markers must already sit at the citation points: `{{zref:ITEMKEY}}` (grouped:
   `{{zref:KEY1;KEY2}}`, alias `[@ITEMKEY]`). Keys come from `zotero_lib.py --search`.
   Grammar definition: `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-zref-protocol.md`.
2. Run the command above.
3. Journal-specific fine style → the `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-styles.md` flow (local CSL → Style
   Repository). **This agent** applies the format; it is handed to no one else. In field mode the
   user can also change the style straight from the Zotero application.
4. Before delivery (only if the journal asks), pin the citations: in field mode Zotero's own
   **Unlink Citations** button; in text mode `--action unlink`.

## Guarantees the caller relies on

- **The source file is never overwritten by default.** Without `--out` the result goes to
  `<ad>_zref.docx` beside it; the JSON report gives that path as `output` — **carry it to the next
  step**. An explicit `--out` aimed back at the source takes a `.bak` copy first (reported as
  `backup`).
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

## Red-revision rule (global)

Updating an **existing** document colours every inserted run red (RGB 255,0,0). Pass `--no-red`
only for a brand-new document built from scratch.

## Zotero concept mapping

| Zotero button | Here |
|---|---|
| Add/Edit Citation | `{{zref:ITEMKEY}}` marker + `zotero_cite.py` |
| Add/Edit Bibliography | `--action refresh` (writes "Kaynaklar" at the end) |
| Refresh (smart text) | every `refresh` call renumbers + updates the bibliography |
| Unlink Citations | `--action unlink --mode text`. In `--mode field` the script refuses, points at Zotero's own button, prints one JSON and saves nothing |
| Style Repository | `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/references/zotero-r-styles.md` |
