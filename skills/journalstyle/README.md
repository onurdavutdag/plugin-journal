<!-- Oluşturma: 20260725 0056 -->
# journalstyle — skill README

Reformats a source `.docx` manuscript to a target journal's author guidelines and reports what
still needs a manual check. Mechanical format only — it never touches citations or the bibliography.

## When it triggers

Turkish trigger phrases (from the SKILL.md `description`): *"bu makaleyi [dergi adı] için formatla"*,
*"dergi şablonuna uydur"*, *"submission için hazırla"*, *"yazar kılavuzuna göre düzenle"*. Also runs
per journal when the same manuscript is prepared for several journals.

## Input / output

- **Input:** source `.docx` + target journal name (+ article type, if given).
- **Output:** `<workspace>/ciktilar/<manuscript>_<slug>.docx` + a compliance report that opens with
  the mandatory provenance block.
- **Workspace:** the folder containing the source `.docx`. `scripts/journalstyle_workspace.py` resolves and
  scaffolds it (`yayinstili/`, `authorguidelines/`, `ciktilar/`). Each profile is cached beside the
  source it was extracted from: `authorguidelines/<slug>.json`, `yayinstili/<slug>.yayinstili.json`.

## Subagents it calls

| Agent | Tools | When | Produces |
|---|---|---|---|
| `journal-s-authorguidelines` | WebSearch, WebFetch, Read | no profile cached for the journal | `web_findings` + `pdf_findings` + a short `webpdf_ozet` — **unmerged**; carries no `Write`, so the skill writes the final `<slug>.json` after the user checkpoint |
| `journal-s-yayinstili` | WebSearch, WebFetch, Read, Write, Bash | official profile ready **and** `<slug>.yayinstili.json` missing or stale | writes `<slug>.yayinstili.json` itself, returns a style summary — de-facto table/figure counts, caption style, reference count, tense/voice, citation density |
| `journalstyle-s-docxformat` | Bash, Read, Write, Edit | profile ready, formatting stage | the formatted `.docx` via `scripts/journalstyle_apply_profile.py`; checks section order / missing sections |

## Constraints

- Never fabricates a journal rule — an unverifiable field stays `null` and the user is warned.
- Citations/bibliography are **`journal-s-zotero`'s authority alone**; this skill only passes `citation_style` on.
- Backs up the original before touching a docx.
- The in-plugin `references/journal-profiles/` holds only the `_example-mdpi.json` template; live
  profiles live in the workspace.

## Files

- `SKILL.md` — the pipeline.
- `references/journalstyle-r-authorguidelines.md` — official rule profile schema.
- `references/journalstyle-r-yayinstili.md` — de-facto publication style schema.
- `scripts/` — `journalstyle_workspace.py`, `journalstyle_apply_profile.py`, `journalstyle_extract_docx_structure.py`, `journalstyle_extract_pdf_text.py`,
  `journalstyle_docx_util.py` (shared helper the other three import: paragraph walk that also covers table cells,
  headers and footers; inline + anchored figure count; utf-8 stdout).
