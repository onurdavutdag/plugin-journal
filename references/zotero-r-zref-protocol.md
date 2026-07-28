# zref handoff protocol — OWNER: journal-s-zotero

The **single marker contract** between the skill that writes the text (`journalwriter`) and the agent that writes the
citations/bibliography (`journal-s-zotero`) is defined here. `journalwriter`/`journalresearch`/`journalstyle` only **write** the marker;
the sole authority that turns the marker into a visible citation and bibliography is `journal-s-zotero` (`zotero_docxatifbas.py`).
For the in-text citation/bibliography **format**: `zotero-r-citation-format.md`. For the marker **grammar**: this file.

## Grammar (verified from the code)

`zotero_docxatifbas.py` parses the markers with this regex:

```
MARKER_RE = re.compile(r"\{\{zref:([A-Z0-9;\s]+)\}\}|\[@([A-Z0-9;\s]+)\]")
```

So two equivalent forms are supported:

| Form | Single | Grouped (multiple sources in the same sentence) |
|---|---|---|
| **Canonical** (write this) | `{{zref:ITEMKEY}}` | `{{zref:KEY1;KEY2}}` |
| Accepted alias (Pandoc) | `[@ITEMKEY]` | `[@KEY1;KEY2]` |

- **`ITEMKEY`** = the 8-character uppercase-letter/digit Zotero item key (e.g. `F5RI4K5K`).
  Found with `zotero_kutuphaneoku.py --search "term"`.
- In a grouped citation, the keys are separated by a **semicolon** (`;`); a space may be added.
- **The writing skill always writes the canonical form (`{{zref:ITEMKEY}}`).** The `[@...]` form is parsed for backward
  compatibility (e.g. text coming from Pandoc); do not use it in new text.

## Who writes what

- **journalwriter / journalresearch / journalstyle:** places `{{zref:ITEMKEY}}` at the exact point where the sentence is supported.
  It does **not write** a raw number (`[1]`), `(Author, Year)`, or a bibliography list — that is `journal-s-zotero`'s job.
  For a source without a key: first have it added to the library with `zotero-r-add-methods.md`, get the key, then write it.
- **journal-s-zotero (`zotero_docxatifbas.py`):** turns each marker into an in-text citation in the selected style, numbers it by
  order of appearance, and writes the bibliography at the end.

## Render behavior (clear contract)

- **Field mode (default, `--mode field`):** each marker becomes a real Zotero Word field
  (`ADDIN ZOTERO_ITEM CSL_CITATION` + `ZOTERO_PREF` + `ZOTERO_BIBL`). The user's Zotero
  application recognizes it; renumbering/style change is done from the Zotero tab in Word.
  A repeated call turns **only NEW markers** into fields; it does not touch existing `ZOTERO_*` fields.
- **Text mode (`--mode text`):** static text; a repeated call = Refresh (renumbers,
  rewrites the bibliography). **Idempotent** within the script — the markers stay in the document.
- **Missing key:** a key not found in the library is **not fabricated**; it is listed under `unknown_keys`
  in the JSON report in the `zotero_docxatifbas.py` output. The writing skill fixes this key or
  adds the source with `zotero-r-add-methods.md`.
- **Duplicate source:** same DOI/PMID = same article; de-duplication is done **during render**
  (see `zotero-r-citation-format.md` → "De-duplication"). Write the **same** key for the same source everywhere.
- **Red revision:** when an existing docx is updated, the added citation/bibliography text is red
  (global rule); `--no-red` in a document from scratch.

## Summary rule

The single canonical marker is `{{zref:ITEMKEY}}`; the grammar is in this file, the format in `zotero-r-citation-format.md`,
adding to the library in `zotero-r-add-methods.md`. No other component formats citations/bibliography.
