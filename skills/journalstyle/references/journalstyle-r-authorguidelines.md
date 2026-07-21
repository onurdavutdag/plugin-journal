# Journal Profile Schema

This is the JSON structure the `journalstyle-s-authorguidelines` agent must produce and the `journalstyle` skill must read. Unknown/unverifiable fields are left `null`, not fabricated.

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
- **Web + PDF flow (checkpoint):** the `journalstyle-s-authorguidelines` agent **always performs a web search**;
  if a PDF exists in the workspace, it also extracts from it **separately** and returns **two separate sets**:
  `web_findings` + `pdf_findings` (+ a short `web_ozet`). The agent **does not merge** them and does not write the final
  `<slug>.json`. The skill shows `web_ozet` to the user and takes the *merge / web only / PDF
  only / manual* decision, then writes the final single profile to `<profiles_dir>/<slug>.json` and
  sets `guidelines_source` per the decision. Conflicts (web vs PDF) are written into `notes`.
