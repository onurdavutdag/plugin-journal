---
name: journalstyle
description: Bu skill, bir .docx makalesini belirli bir akademik derginin (Elsevier, MDPI, IEEE, Springer, Türkçe ULAKBİM dergileri vb.) yazar kurallarına göre biçimlendirmek gerektiğinde kullanılmalıdır. Tetikleyiciler; "bu makaleyi [dergi adı] için formatla", "dergi şablonuna uydur", "submission için hazırla", "yazar kılavuzuna göre düzenle" gibi ifadeler. Birden fazla dergiye aynı makaleyi hazırlamak için de kullanılır (her dergi için ayrı profil ve ayrı çıktı üretir).
---

# Journal Style

This skill runs a **pipeline** to produce, from a single source `.docx` manuscript, a `.docx` output that conforms to the target journal's rules. It delegates to two sub-agents and uses a profile cache to avoid repeated searches.

## Flow

0. **Resolve the workspace (before everything else).** The plugin now runs every job through the
   **folder containing the source `.docx`**. Call the following, passing the source `.docx` path (and the journal slug if it is already known):
   `PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/journalstyle_workspace.py" "<source.docx>" --slug <slug>`
   (`${CLAUDE_PLUGIN_ROOT}` gives the plugin root; in a global install cwd is the workspace, so scripts
   are called with this variable — a relative `scripts/...` path breaks globally.)
   The script **auto-creates** (idempotent) the `yayinstili/`, `authorguidelines/`, `ciktilar/`
   folders and a `README.md` placeholder if missing, and prints a JSON to stdout. Use the **absolute
   paths** in this JSON (`authorguidelines_dir`, `yayinstili_dir`, `yayinstili_slug_dir`,
   `authorguidelines_slug_dir`, `outputs_dir`) and the PDF lists (`yayinstili_pdfs`,
   `authorguidelines_pdfs`) for the rest of the flow.
   Once the slug becomes known in Step 2, call the script again with `--slug` to have the subfolders set up.
   **Each profile sits beside the source it came from** — `authorguidelines/<slug>.json` next to the
   guideline PDFs, `yayinstili/<slug>.yayinstili.json` next to the sample article PDFs. There is no
   separate profile folder.
   **Do NOT use the in-plugin `references/journal-profiles/` / `references/yayinstili-pdf/` paths anymore**
   — they have all moved to the workspace.
   If the JSON reports a non-empty **`legacy_dirs`**, the workspace still carries the pre-1.16.0 layout
   (`authorguidelines-pdf/`, `yayinstili-pdf/`, `journal-profiles/`). Nothing is moved automatically —
   tell the user which folders to move and where.

1. **Clarify the target.** Get the target journal name from the user (and the article type if any: research article, review, case report, etc.). If multiple journals are given, run this flow separately for each.

2. **Find or create the profile.** Follow **"Call procedure (checkpoint)"** in
   `references/journalstyle-r-authorguidelines.md`: cache check (6 months) → agent call → user
   checkpoint → write. That section is the single description of the flow, shared with `journalwriter`;
   do not restate it here.
   **Red rule:** the agent returns `web_findings` + `pdf_findings` **unmerged** and never writes
   `<slug>.json`. Per the user's decision **this skill** builds the final profile and saves it to
   `<authorguidelines_dir>/<journal-slug>.json` with the matching `webpdf_source`.

2.5. **Analyze the publication style.** Once the official profile is ready, follow **"Call procedure"**
   in `references/journalstyle-r-yayinstili.md`: cache check → agent call → use the returned style
   frame. A fresh `<yayinstili_dir>/<journal-slug>.yayinstili.json` is used **without calling the agent**;
   only when it is older than 6 months ask the user whether to re-analyze.
   **Red rule:** unlike the official profile, `journal-s-yayinstili` **writes its own file** — there is
   no user decision to gate it. This step only gathers information, does not touch the text, and does
   not override the official rule profile (`<slug>.json`).
   **Tip:** the user controls the style source by adding PDFs from the target journal to the workspace's
   `yayinstili/<slug>/` folder (the `<yayinstili_slug_dir>` set up by Step 0). A specific sample
   article (file/URL/DOI, e.g. "look at the style of this article") goes to the agent as
   `user_reference_article`.

3. **Analyze the source document.** With `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/journalstyle_extract_docx_structure.py`, extract the current `.docx`'s structure (headings, sections, citation style, table/figure count, word count). Compare it against the profile's requirements; if a section is missing (e.g. "Highlights", "Data Availability Statement", "Declaration of Interest"), name the missing ones to the user and ask whether to add them as empty placeholders. **Adding them is `journalstyle-s-docxformat`'s job in Step 4** (`journalstyle_apply_profile.py … --add-sections`) — this skill never opens the docx itself, and no heading is added without the user's answer.

4. **Apply the formatting.**
   - For mechanical rules like page layout, font, line spacing, margins, heading styles, call the **journalstyle-s-docxformat** subagent together with the profile's `formatting` block. This agent uses the `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/journalstyle_apply_profile.py` script (python-docx based). The **output `.docx`** is written under Step 0's `<outputs_dir>` (workspace `ciktilar/`) as `<manuscript>_<slug>.docx`; give the agent the output path from this directory. If Step 3 found missing required sections **and the user approved adding them**, say so in the brief — the agent re-runs the script with `--add-sections`, which appends each one as a real Word heading + placeholder at the end of the file. Section **order** is reported, never rearranged automatically (content-loss risk).
   - **Citation/bibliography is NOT this skill's job.** Adding/removing/updating in-text citations and the bibliography list in a docx, and the style conversion (APA/Vancouver/IEEE/Chicago, etc.), are **the `journal-s-zotero` agent's authority alone.** Pass the `citation_style` info from the journal profile to `journal-s-zotero` (Task); leave the docx citation/bibliography work to it. This skill never touches the bibliography.

5. **Verify and report.** **Start the report with the provenance block** (see "Report provenance"). After applying, run `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/journalstyle_extract_docx_structure.py` again and check against the profile requirements (word limit, required sections). Verifying and fixing reference/citation **format is `journal-s-zotero`'s job** — here only add a note "is the citation style compatible with the journal, and if not, direct to `journal-s-zotero`". Give the user a short "compliance report": list what was fixed automatically, what needs a manual check (e.g. figure/table placement, copyright permissions, `journal-s-zotero` for citation/bibliography). Also, in the report, **compare** the source manuscript's de-facto table/figure/reference count and style with the journal's typical values (`<slug>.yayinstili.json`) (e.g. "this journal has a median of 3 tables, the draft has 7 tables — simplification could be considered"; "the journal places the figure caption below the visual, the draft has it above").

6. **Multi-journal scenario.** If the same manuscript is prepared for multiple journals, produce separate outputs as `<outputs_dir>/<manuscript-name>_<journal-slug>.docx`, starting from a clean copy of the source each time. Each journal shares its own `<slug>/` subfolder (yayinstili, authorguidelines) and profiles within the same workspace. State any non-shared requirements (e.g. word limit difference) separately in the report.

## Report provenance (required)

Every report presented to the user starts, right under the title, with this provenance block; it lists
the subagents **actually** called and the references **actually** read in that job (unused → `—`):

```
Skill: journalstyle
Subagent: <the ones called: journal-s-authorguidelines / journal-s-yayinstili / journalstyle-s-docxformat>
References: <the ones read: journalstyle-r-authorguidelines.md / journalstyle-r-yayinstili.md>
---
```

## Important rules

- Never fabricate an unverified journal rule. If `journal-s-authorguidelines` cannot verify a rule, leave the relevant field in the profile as `null` and warn the user — do not silently assume.
- The profile cache is now stored **in the workspace, beside its own source** — the rule profile in `<authorguidelines_dir>` (`<workspace>/authorguidelines/<slug>.json`), the de-facto style in `<yayinstili_dir>` (`<workspace>/yayinstili/<slug>.yayinstili.json`) — both resolved with `journalstyle_workspace.py` in Step 0. The in-plugin `references/journal-profiles/` is **not used** (only the `_example-mdpi.json` template sits there as an example).
- Always back up the original file before touching the docx (`<name>_original_backup.docx`).

## Additional Resources

### Reference Files

- **`references/journalstyle-r-authorguidelines.md`** — the official rule profile schema (what
  `journal-s-authorguidelines` fills in).
- **`references/journalstyle-r-yayinstili.md`** — the de facto publication-style schema (what
  `journal-s-yayinstili` fills in).
- **`references/journal-profiles/_example-mdpi.json`** — a filled-in profile template for reference only;
  live profiles belong to the workspace.
- **No PDF is kept in the plugin.** Sample article and author-guideline PDFs live in the workspace
  (`yayinstili/<slug>/`, `authorguidelines/<slug>/` next to the source `.docx`). `.gitignore`
  keeps `*.pdf` out of git, but `marketplace update` + `install` copy the whole tree regardless — so a
  publisher PDF placed inside the plugin would be replicated into every installed version folder.

### Scripts

- **`scripts/journalstyle_workspace.py`** — resolves the workspace from the source `.docx` and scaffolds the subfolders.
- **`scripts/journalstyle_apply_profile.py`** — applies the mechanical format (font, size, spacing, margins, page).
- **`scripts/journalstyle_extract_docx_structure.py`** — headings, word count, table/figure count, current margins.
- **`scripts/journalstyle_extract_pdf_text.py`** — sample-PDF text and metrics for `journal-s-yayinstili`.

Call all scripts as `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/<name>.py` — in a global
install cwd is the workspace, so a relative path breaks.
