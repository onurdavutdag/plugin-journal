---
name: journalstyle
description: Bu skill, bir .docx makalesini belirli bir akademik derginin (Elsevier, MDPI, IEEE, Springer, Türkçe ULAKBİM dergileri vb.) yazar kurallarına göre biçimlendirmek gerektiğinde kullanılmalıdır. Tetikleyiciler; "bu makaleyi [dergi adı] için formatla", "dergi şablonuna uydur", "submission için hazırla", "yazar kılavuzuna göre düzenle" gibi ifadeler. Birden fazla dergiye aynı makaleyi hazırlamak için de kullanılır (her dergi için ayrı profil ve ayrı çıktı üretir).
---

# Journal Style

This skill runs a **pipeline** to produce, from a single source `.docx` manuscript, a `.docx` output that conforms to the target journal's rules. It delegates to two sub-agents and uses a profile cache to avoid repeated searches.

## Flow

0. **Resolve the workspace (before everything else).** The plugin now runs every job through the
   **folder containing the source `.docx`**. Call the following, passing the source `.docx` path (and the journal slug if you know it):
   `PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/workspace.py" "<source.docx>" --slug <slug>`
   (`${CLAUDE_PLUGIN_ROOT}` gives the plugin root; in a global install cwd is the workspace, so scripts
   are called with this variable — a relative `scripts/...` path breaks globally.)
   The script **auto-creates** (idempotent) the `yayinstili-pdf/`, `authorguidelines-pdf/`, `journal-profiles/`, `ciktilar/`
   folders and a `README.md` placeholder if missing, and prints a JSON to stdout. Use the **absolute
   paths** in this JSON (`profiles_dir`, `yayinstili_slug_dir`, `authorguidelines_slug_dir`,
   `outputs_dir`) and the PDF lists (`yayinstili_pdfs`, `authorguidelines_pdfs`) for the rest of the flow.
   If you learn the slug in Step 2, call the script again with `--slug` to have the subfolders set up.
   **Do NOT use the in-plugin `references/journal-profiles/` / `references/yayinstili-pdf/` paths anymore**
   — they have all moved to the workspace.

1. **Clarify the target.** Get the target journal name from the user (and the article type if any: research article, review, case report, etc.). If multiple journals are given, run this flow separately for each.

2. **Find or create the profile.**
   - First look at `<profiles_dir>/<journal-slug>.json` (the absolute path from Step 0). If it exists and
     is older than 6 months, ask the user "should I use the cached profile or search the current rules again?"
   - If not, call the **journalstyle-s-authorguidelines** subagent. Pass it: journal name
     + slug + (if any) article type + **the PDF paths in `authorguidelines_slug_dir`**
     (`authorguidelines_pdfs`, if any) + `profiles_dir`. The agent **performs a web search in every case**;
     it also reads a PDF with `Read` if one is given, and returns the two findings **without merging them**
     (`web_findings`, `pdf_findings` + a short web summary). See `references/journalstyle-r-authorguidelines.md`.
   - **CHECKPOINT (user approval — required, not skipped):** **Show the user the web result summary**
     the agent returned. Then ask: *should I merge the PDF with the web, or just web / just PDF
     / manual correction?* If there is no PDF, the output is web-only, but **still show the web summary**
     and get approval.
   - Per the user's decision, **you** build the final profile and save it under
     `<profiles_dir>/<journal-slug>.json` (set the `guidelines_source` field to `web` / `user-pdf` / `both-merged` per the decision).

2.5. **Analyze the publication style.** Once the official profile is ready, call the **journalstyle-s-yayinstili**
   subagent: give it the journal name + slug + official profile + **the source `.docx`'s topic/keywords**
   (extract from title/abstract/keywords) + the **`yayinstili_slug_dir`** and **`profiles_dir`** absolute
   paths from Step 0. The agent extracts the style **first from the user's uploaded sample PDFs under
   `<yayinstili_slug_dir>`** (the primary source, `style_source: "user-pdf"`); if this folder is
   missing/empty, it falls back to 3–6 open-access sample articles from the journal from the last 5 (else
   last 10) years via the web as a **backup** (`style_source: "journal-auto"`). It produces the result as
   `<profiles_dir>/<journal-slug>.yayinstili.json` (de-facto
   table/figure count and numbering, caption style, reference count, section headings, text
   tense/voice, citation density, statistics presentation — see `references/journalstyle-r-yayinstili.md`).
   If this file exists and is fresh, do not re-run; ask the user. This step **only gathers information,
   does not touch the text** — it does not override the official rule profile (`<slug>.json`), it writes to a separate file.
   **Tip:** the user can control the style source directly by adding PDFs from the target journal to the
   workspace's `yayinstili-pdf/<slug>/` folder (the `<yayinstili_slug_dir>` set up by Step 0). If the user gave a specific sample article
   (file/URL/DOI, e.g. "look at the style of this article"), pass it to the agent as `user_reference_article`;
   the agent takes it as a primary style source too.

3. **Analyze the source document.** With `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/extract_docx_structure.py`, extract the current `.docx`'s structure (headings, sections, citation style, table/figure count, word count). Compare it against the profile's requirements; if a section is missing (e.g. "Highlights", "Data Availability Statement", "Declaration of Interest"), notify the user and say you can add an empty template automatically.

4. **Apply the formatting.**
   - For mechanical rules like page layout, font, line spacing, margins, heading styles, call the **journalstyle-s-docxformat** subagent together with the profile's `formatting` block. This agent uses the `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/apply_profile.py` script (python-docx based). The **output `.docx`** is written under Step 0's `<outputs_dir>` (workspace `ciktilar/`) as `<manuscript>_<slug>.docx`; give the agent the output path from this directory.
   - **Citation/bibliography is NOT this skill's job.** Adding/removing/updating in-text citations and the bibliography list in a docx, and the style conversion (APA/Vancouver/IEEE/Chicago, etc.), are **the `zotero` skill's authority alone.** Pass the `citation_style` info from the journal profile to `zotero`; leave the docx citation/bibliography work to `zotero`. This skill never touches the bibliography.

5. **Verify and report.** **Start the report with the provenance block** (see "Report provenance"). After applying, run `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/extract_docx_structure.py` again and check against the profile requirements (word limit, required sections). Verifying and fixing reference/citation **format is `zotero`'s job** — here only add a note "is the citation style compatible with the journal, and if not, direct to zotero". Give the user a short "compliance report": list what was fixed automatically, what needs a manual check (e.g. figure/table placement, copyright permissions, `zotero` for citation/bibliography). Also, in the report, **compare** the source manuscript's de-facto table/figure/reference count and style with the journal's typical values (`<slug>.yayinstili.json`) (e.g. "this journal has a median of 3 tables, the draft has 7 tables — simplification could be considered"; "the journal places the figure caption below the visual, the draft has it above").

6. **Multi-journal scenario.** If the same manuscript is prepared for multiple journals, produce separate outputs as `<outputs_dir>/<manuscript-name>_<journal-slug>.docx`, starting from a clean copy of the source each time. Each journal shares its own `<slug>/` subfolder (yayinstili-pdf, authorguidelines-pdf) and profiles within the same workspace. State any non-shared requirements (e.g. word limit difference) separately in the report.

## Report provenance (required)

Every report presented to the user starts, right under the title, with this provenance block; it lists
the subagents **actually** called and the references **actually** read in that job (unused → `—`):

```
Skill: journalstyle
Subagent: <the ones called: journalstyle-s-authorguidelines / journalstyle-s-yayinstili / journalstyle-s-docxformat>
References: <the ones read: journalstyle-r-authorguidelines.md / journalstyle-r-yayinstili.md>
---
```

## Important rules

- Never fabricate a journal rule you are unsure of. If `journalstyle-s-authorguidelines` cannot verify a rule, leave the relevant field in the profile as `null` and warn the user — do not silently assume.
- The profile cache is now stored **in the workspace** under `<profiles_dir>` (`<workspace>/journal-profiles/`) — resolved with `workspace.py` in Step 0. The in-plugin `references/journal-profiles/` is **not used** (only the `_example-mdpi.json` template sits there as an example).
- Always back up the original file before touching the docx (`<name>_original_backup.docx`).
