# Journal Profile Schema

This is the JSON structure the `journal-s-authorguidelines` agent must produce and the `journalstyle` skill must read. Unknown/unverifiable fields are left `null`, not fabricated.

```json
{
  "journal_name": "Journal of Example Research",
  "publisher": "Elsevier",
  "source_url": "https://www.elsevier.com/journals/.../guide-for-authors",
  "last_verified": "2026-07-05",
  "guidelines_source": "web",
  "article_types": ["research article", "review"],
  "word_limit": {
    "value": 8000,
    "excludes": ["references", "abstract", "figure captions"]
  },
  "abstract": {
    "max_words": 250,
    "structured": false,
    "keywords_min": 4,
    "keywords_max": 6
  },
  "formatting": {
    "font_family": "Times New Roman",
    "font_size_pt": 12,
    "line_spacing": "double",
    "margins_cm": {"top": 2.5, "bottom": 2.5, "left": 2.5, "right": 2.5},
    "page_size": "A4",
    "heading_style": "numbered",
    "line_numbers": true
  },
  "section_order": [
    "Title Page", "Abstract", "Keywords", "Introduction", "Methods",
    "Results", "Discussion", "Conclusion", "Declarations",
    "References", "Tables", "Figures"
  ],
  "required_sections": [
    "Declaration of Competing Interest", "Data Availability Statement",
    "Author Contributions", "Funding"
  ],
  "citation_style": {
    "name": "Vancouver",
    "in_text": "numbered",
    "reference_list_style": "numbered-order-of-appearance"
  },
  "figures_tables": {
    "placement": "end-of-manuscript",
    "numbering": "Figure 1, Figure 2 ...",
    "caption_position": "below-figure-above-table"
  },
  "file_format": {
    "accepted": [".docx", ".tex"],
    "figure_formats": [".tiff", ".eps", ".png (min 300dpi)"]
  },
  "notes": "Free text for points that remain unverifiable or unclear."
}
```

## Filling rules

- `source_url` must be the real "Author Guidelines" page; a general journal home page is not accepted.
- `last_verified` is updated on every search; the skill suggests re-verification to the user for profiles older than 6 months.
- Non-numeric/complex rules (e.g. "an additional document is required if figure copyright permission is needed") are written into the `notes` field; `apply_profile.py` does not apply these automatically — they are reported to the user as a manual step.
- **`guidelines_source`** indicates the rule's source: `"web"` = web search only; `"user-pdf"` =
  only the workspace's `authorguidelines-pdf/<slug>/` PDF; `"both-merged"` = the user chose at the checkpoint
  to merge web + PDF; `"both-unmerged"` = the **draft** stage the agent returned (not yet
  merged).
- **Web + PDF flow (checkpoint):** see "Call procedure (checkpoint)" below — the single description
  of the flow, followed by both `journalstyle` and `journalwriter`.

## Call procedure (checkpoint)

This procedure is the **single** source for both callers (`journalstyle` step 2, `journalwriter`
step 2). Neither SKILL.md repeats it; they point here.

**1. Cache first.** Read `<profiles_dir>/<slug>.json` (`profiles_dir` comes from `workspace.py`).
- Present and `last_verified` newer than 6 months → use it, **do not call the agent**.
- Present but older than 6 months → ask the user: use the cached profile, or search the rules again?
- Absent → continue to step 2.

**2. Call the agent.** Pass `journal-s-authorguidelines`: journal name · slug · article type (if
any) · `profiles_dir` · `authorguidelines_pdfs` (the absolute PDF paths under
`authorguidelines-pdf/<slug>/`, if any).

**3. What comes back.** The agent **always performs a web search**, and additionally reads the PDF
if one was given. It returns **two separate sets** — `web_findings` + `pdf_findings` — plus a short
readable `web_ozet`. It **does not merge** them and it **does not write** `<slug>.json`; conflicts
(web says 3000 words, PDF says 3500) are recorded in `notes`, not resolved.

**4. Checkpoint — required, never skipped.** Show the user `web_ozet`, then ask: *merge the PDF with
the web / web only / PDF only / manual correction?* If there is no PDF the result is web-only —
**still show the summary and get approval**.

**5. The skill writes.** Per the user's decision the **calling skill** — not the agent — builds the
single final profile and saves it to `<profiles_dir>/<slug>.json`, stamping `guidelines_source`
(`web` / `user-pdf` / `both-merged`) and `last_verified`.

**Why the skill writes:** the decision belongs to the user and arrives after the agent's run has
ended. A sub-agent cannot address the user, and re-invoking it would mean transporting both finding
sets into a cold context. The caller already holds them, so the write costs it one tool call.
