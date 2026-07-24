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
- **Workspace:** the folder containing the source `.docx`. `scripts/workspace.py` resolves and
  scaffolds it (`yayinstili-pdf/`, `authorguidelines-pdf/`, `journal-profiles/`, `ciktilar/`).

## Subagents it calls

| Agent | Tools | When | Produces |
|---|---|---|---|
| `journalstyle-s-authorguidelines` | WebSearch, WebFetch, Read, Write | no profile cached for the journal | `web_findings` + `pdf_findings` + a short web summary — **unmerged**; the skill writes the final `<slug>.json` after the user checkpoint |
| `journalstyle-s-yayinstili` | WebSearch, WebFetch, Read, Write, Bash | after the official profile is ready | `<slug>.yayinstili.json` — de-facto table/figure counts, caption style, reference count, tense/voice, citation density |
| `journalstyle-s-docxformat` | Bash, Read, Write, Edit | profile ready, formatting stage | the formatted `.docx` via `scripts/apply_profile.py`; checks section order / missing sections |

## Constraints

- Never fabricates a journal rule — an unverifiable field stays `null` and the user is warned.
- Citations/bibliography are **`zotero`'s authority alone**; this skill only passes `citation_style` on.
- Backs up the original before touching a docx.
- The in-plugin `references/journal-profiles/` holds only the `_example-mdpi.json` template; live
  profiles live in the workspace.

## Files

- `SKILL.md` — the pipeline.
- `references/journalstyle-r-authorguidelines.md` — official rule profile schema.
- `references/journalstyle-r-yayinstili.md` — de-facto publication style schema.
- `scripts/` — `workspace.py`, `apply_profile.py`, `extract_docx_structure.py`, `extract_pdf_text.py`.
