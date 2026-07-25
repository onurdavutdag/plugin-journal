<!-- Oluşturma: 20260725 0056 -->
# writer — skill README

Writes one section of an academic manuscript (Introduction / Methods / Results / Discussion /
Abstract / Conclusion) in the target journal's style and the user's own voice. The only skill in the
plugin that produces text.

## When it triggers

Turkish trigger phrases (from the SKILL.md `description`): *"tartışma bölümünü yaz"*, *"giriş yaz"*,
*"sonuç bölümünü yaz"*, *"bu dergi için özet yaz"*, *"makale metni oluştur"*,
*"şu bölümü [dergi adı] stiline göre yaz"*. Formatting-only requests go to `journalstyle` instead.

## Input / output

- **Input:** which section · target journal (+ article type) · source `.docx`/thesis/results ·
  language of the source text.
- **Output:** the written section with `{{zref:ITEMKEY}}` citation markers, plus an auditable list of
  every added citation (supported sentence · reference · why · evidence level · source · DOI/PMID).
  Output opens with the mandatory provenance block.

## What it calls automatically (no separate user command)

| Called | Type | When | Purpose |
|---|---|---|---|
| `writer-s-danisman` | agent (Read, Grep, Glob) | before writing, always | IMRaD skeleton + reporting guideline (STROBE/CONSORT/STARD/CARE/PRISMA/ARRIVE) + section-specific common mistakes. Produces **no** citations. |
| `journalstyle-s-yayinstili` | agent | before writing, always | de-facto journal style: tense/voice, citation density, headings, statistics presentation |
| `journalstyle-s-authorguidelines` | agent | conditional — no cached profile | the official rule profile (web + PDF checkpoint) |
| `research` | skill | every evidence-needing claim without a user citation | a real, verified DOI/PMID |
| `zotero` (`zotero_cite.py`) | skill | when the section is written into a docx | in-text citations + bibliography |
| `journal-s-notebooklm` | agent (file tools + notebooklm-mcp) | Introduction and Discussion | owns all NotebookLM interaction: background/gap material (Introduction) + literature-comparison material (Discussion) — content, never a citation |

## Constraints

- **Never fabricates a citation** — the skill's single red line. Verification belongs to `research`.
- Writes only the `{{zref:KEY}}` marker; never a raw `[1]` / `(Author, Year)`, never a hand-kept
  bibliography — that is `zotero`'s authority alone.
- Preserves the user's voice and language; keeps citations the user already inserted.
- Number/percentage/p-value format follows the user's language-dependent global rule.

## Files

- `SKILL.md` — the flow.
- `references/writer-s-danisman-r-bilgi.md` — distilled manuscript-writing knowledge (the advisor's source).
- `references/writer-s-danisman-r-guidelines/` — ARRIVE · CARE · CONSORT · PRISMA · STARD · STROBE,
  item level. Also **reused read-only by `peerreview`**.
