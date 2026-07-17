# Searching uploaded PDFs

The author's own uploaded literature is **tier 2** in the evidence priority (after
references they explicitly supplied, before any external search). Prefer citing these
papers when they genuinely support the statement — they are the literature the author
already trusts and has read.

## 0. Always scan the user's fixed library — `pdflerim/`

This skill ships a dedicated folder, `pdflerim/`, in its own directory (`<research-skill-dir>/pdflerim/`).
It is the author's **curated PDF library** — papers they deliberately dropped in for this work.
Scan it on **every** citation task, in addition to the general workspace discovery below, and
before descending to any external search:

```
python scripts/search_pdfs.py --dir <research-skill-dir>/pdflerim --terms "concept one" "keyword" ...
```

- Run this **separately and always**, even when a workspace/project PDF search also runs — the
  two are additive, not either/or.
- If `pdflerim/` is empty, the script returns `[]`; **skip silently** (not an error) and continue
  with the general workspace/Drive discovery in step 1.
- Treat every hit exactly like any other PDF hit: **confirm with the Read tool** (step 3) before
  citing — keyword overlap is not support. The output `Source` label stays `Uploaded PDF`; you may
  note the `pdflerim` sub-source inside the justification.
- Build `--terms` from the target sentence using the rules in step 2.

## 1. Discover the PDFs

Find every PDF available to the current project/workspace:

- **Fixed library**: `pdflerim/` (see step 0) is always included — don't skip it here.
- **Local project/workspace**: use `Glob` with `**/*.pdf` from the project root (and any
  folder the user points at). Also check an `assets/` or `references/` subfolder if present.
- **Zotero dermesi (kullanıcının adını verdiği collection)**: tier-2 kanıt. **Tüm Zotero
  kütüphanesini tarama** — yalnız kullanıcının işaret ettiği dermeyi kullan.
  0. **Derme adı verilmediyse MUTLAKA sor** — sessizce tüm kütüphaneyi tarama, sessizce de
     atlama. `python <zotero-skill-dir>/scripts/zotero_lib.py --list-collections` ile mevcut
     dermeleri listeleyip kullanıcıya hangisini kullanacağını sor; cevabı bekle.
  1. `python <zotero-skill-dir>/scripts/zotero_lib.py --items --collection "<derme-adı>"` ile
     o dermenin item'larını al; her item'ın `attachments` alanı gerçek `storage/<KEY>/*.pdf`
     yollarını verir.
  2. **Yalnız o attachment yollarını** oku: az sayıdaysa doğrudan Read ile, çoklarsa her item'ın
     `storage/<KEY>` klasörünü `search_pdfs.py --dir` ile tara. Storage kökünü tümüyle tarama.
  3. Künye (DOI/PMID) item kaydından gelir — uydurma yok; eksikse PubMed
     `lookup_article_by_citation` ile kurtar. İsabeti step 3'teki gibi Read ile doğrula.
  Kanonik akış ve item↔attachment eşlemesi: `zotero` skill'inin `references/storage-bridge.md`'si.
- **Google Drive** (if the user keeps papers there): `mcp__claude_ai_Google_Drive__search_files`
  to locate PDFs, then `mcp__claude_ai_Google_Drive__read_file_content` /
  `download_file_content` to pull text. Only do this if local search comes up short or the
  user mentions Drive.

Search **every** available PDF — don't stop at the first match. A claim may be supported by
more than one of the author's papers.

## 2. Build search terms

From the target sentence, extract the key concepts: the exposure/intervention, the outcome,
the population, and any specific numbers or named entities (drug, gene, scale, disease).
Pass several terms/phrases so the script can match any of them:

```
python scripts/search_pdfs.py --dir <workspace-or-project-dir> --terms "postoperative delirium" "dexmedetomidine" "ICU" "incidence"
```

Prefer specific multi-word phrases plus a few single keywords. If the first pass misses,
retry with synonyms (e.g., "myocardial infarction" and "MI", "mortality" and "death").

## 3. Interpret hits and confirm with the Read tool

The script returns JSON: `{file, page, section_heading, snippet}` per hit. `section_heading`
is a best-effort nearest heading and may be approximate. **Always confirm** a hit before
citing it:

- Open the PDF at the reported page with the **Read tool** using the `pages` parameter
  (e.g., `pages: "5"` or a small range) to read the surrounding context.
- Verify the passage actually supports the specific claim — not merely shares keywords.
- Note the **real** page number and the true **section heading** (Introduction, Methods,
  Results, Discussion, a named subsection, or a table/figure caption).

If the script reports no extractor is installed, read the candidate PDFs directly with the
Read tool (it renders PDF pages) and locate the passage manually.

## 4. Extract the supporting passage — minimally

- **Summarize** the evidence in your own words; this is what goes in "Why this reference was
  selected."
- **Quote only the minimum text necessary** — usually a single sentence or a reported
  statistic — to establish the point. Do not paste paragraphs.
- **Report page number and section heading** in the output (the `Page number (if PDF)` field
  and inside the justification).

## 5. Feed results into the output

Each supported sentence gets its own recommendation block (see `research-r-kunye.md`), with
`Source: Uploaded PDF` and the page number filled in. If the PDF also carries a DOI/PMID
(often on the first page or in the header/footer), include them — and use PubMed
(`mcp__claude_ai_PubMed__lookup_article_by_citation`) to recover a missing DOI/PMID from the
title + authors + year so the reference is fully verifiable.

## 6. Writing-time collaboration with `writer`

When the `writer` skill is drafting and triggers `research` for a
claim (see writer's §5), **scan `pdflerim/` first** (step 0) with that sentence's terms. Return
each confirmed hit with its **page number and section heading** so the writer can weave the
finding into the prose — not just append a bare number (e.g. "Su et al. likewise reported a drop
in delirium incidence [1]"). The writer places the in-text citation per the journal's
`citation_style` and adds it to the reference list, de-duplicating by DOI/PMID. If `pdflerim/`
yields nothing for the claim, fall through to the general workspace scan and then external search
as usual.
