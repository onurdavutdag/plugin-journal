# yayinstili-pdf — Local publication-style sample articles (OLD / example location)

> **IMPORTANT — the location has changed.** The publication-style sample PDFs are no longer inside the plugin, but
> **in each study's own workspace** (the source `.docx`'s folder) under `yayinstili-pdf/<slug>/`.
> The `journal-s-yayinstili` agent gets this folder from the skill via the `yayinstili_slug_dir` absolute
> path. The workspace is resolved with `skills/journalstyle/scripts/workspace.py` and the folder is
> auto-created if missing. This in-plugin folder sits only as **old/example**; for new jobs use
> the workspace.

The `journal-s-yayinstili` agent extracts a journal's **actual publication conventions** (table/figure
count and numbering, caption position, reference count, section headings, sentence length, citation
form, statistics presentation) from these PDFs. **It is the primary style source**; the web search
runs only as a backup when there is no matching local PDF.

## Usage (in the workspace)

Put the sample articles for the target journal into a **subfolder named after the journal's slug** inside the workspace:

```
yayinstili-pdf/
  <slug>/
    article1.pdf
    article2.pdf
```

- `<slug>` is the **same** as the slug in the `journal-profiles/*.json` files
  (e.g. The Spine Journal → `thespinejournal`).
- 3–6 recent, topic-similar articles is ideal; 1–2 also works (unreliable metrics stay `null`).
- The PDFs must contain a real text layer (text extraction is weak in scanned-image PDFs).

Example: `yayinstili-pdf/thespinejournal/` — 5 The Spine Journal articles.

## Copyright

The agent copies **no sentence/caption/abstract text verbatim** from these PDFs; it extracts only
numeric metrics and structural patterns in rule form. The PDFs are kept locally only for style analysis.
