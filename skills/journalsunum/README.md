<!-- Oluşturma: 20260912 1420 -->
# journalsunum — skill README

Builds an **academic presentation** from the user's own material: congress oral paper,
congress poster, thesis defence, seminar / case presentation / journal club. Decides the
narrative and the slide budget, gets the outline approved, and hands rendering to its
sub-agents. Never draws a slide itself; never fabricates a claim, a citation or a figure.

## When it triggers

Turkish trigger phrases (from the SKILL.md `description`): *"kongre sunumu hazırla"*,
*"bildiri sunumu"*, *"poster hazırla"*, *"70×100 poster"*, *"tez savunması sunumu"*,
*"seminer slaytları"*, *"journal club sunumu"*, *"olgu sunumu"*, *"makaleden sunum çıkar"*,
*"bu desteyi eleştir"*, *"kaç slayt olmalı"*.

**Not** for generic `.pptx` mechanics (open / read / merge any deck) — that is the global
`pptx` skill's job and it triggers on its own phrasing; `/journal` says so when asked.

## Input / output

- **Input:** type · duration (or organiser + printer rules for a poster) · audience · Q&A
  placement · language (always asked) · source material from the checkout's `input/`
  (manuscript docx, thesis, results xlsx/csv, figures, a paper PDF for a journal club).
- **Output:** `<outputs_dir>/<stem>_sunum.pptx` with speaker notes and backup slides, plus
  the generator script and the preview grid; for a poster `<stem>_poster.pptx`, its
  `poster.json` manifest, the audit reports and — with PowerPoint installed — the PDF.
  `input/` is never written. With PowerPoint installed a finished deck is opened on screen
  with the Designer pane for the user's own layout choices, then re-audited after they save.
- **Language:** the slides are in the language the user chose; the outline is shown in it.
- **Own draft:** a `.pptx`/`.potx` the user made goes into `input/pptx/`; the skill reads it,
  critiques it and asks *polish* (`<stem>_v2.pptx`, the draft kept as the template) or *rebuild*
  (a new deck from its content). See SKILL.md → "Draft-deck mode".

## Subagents

| Agent | Job | Tools |
|---|---|---|
| `journalsunum-s-danisman` | Budget, skeleton, citation slots, critique — before any slide is written | Read, Grep, Glob |
| `journalsunum-s-pptx` | Renders / edits / reads the deck by driving the installed `pptx` skill; render → grid → fix loop, the grid through real PowerPoint when installed; Designer hand-off + re-audit | Read, Glob, Grep, Bash, Write, Edit, Skill |
| `journalsunum-s-poster` | Writes the strict manifest, runs the poster pipeline (validate · inventory · palette · export plan · generate · inspect · layout), previews and exports the PDF through PowerPoint after the package inspection passes; fails closed | Read, Glob, Grep, Bash, Write |

Cross-skill calls: `journal-s-zotero` (citation strings for slides), `journal-s-notebooklm`
(literature for seminars), `journalresearch` (an unsourced claim).

## Requirements beyond the package

- **Anthropic `pptx` skill** on the machine — `npx skills add anthropics/skills@pptx -g` —
  with `pptxgenjs` (npm) and `markitdown[pptx]` (pip). It is proprietary and is **not**
  shipped here; the deck agent stops with the install line when it is missing.
- **Microsoft PowerPoint** (optional, detected at run time): the plugin-root
  `scripts/office_kopru.py` drives it through PowerShell COM for the slide preview, the PDF,
  the font check and the Designer hand-off. Without it the preview falls back to the `pptx`
  skill's LibreOffice + Poppler path (`soffice`, `pdftoppm` on `PATH`), and without those it
  is reported as skipped.
- **Poster generation** needs `uv` and runs with exact pins (`python-pptx==1.0.2`,
  `Pillow==12.3.0`, `lxml==6.1.1`) in an isolated environment; the audit scripts run under
  the machine's Python.

## Constraints

- Nothing is rendered before the user approves the outline (deck) or every text verbatim
  and the manifest hash (poster).
- Citation strings on slides come only from `journal-s-zotero`; the docx bibliography
  authority is unchanged.
- The poster agent renders exact approved text and refuses placeholders, unverified sources
  and unconfirmed organiser/printer rules.
- Manual items (PowerPoint Accessibility Checker, printer proof, author sign-off) are handed
  to the user, never claimed.

## Files

- `SKILL.md` — the 8-step flow, critique mode, routing table.
- `references/journalsunum-r-yapi.md` · `-r-konusma.md` · `-r-tasarim.md` · `-r-poster.md`
  · `-r-postermanifest.md` + `journalsunum-poster-manifest-ornek.json`.
- `scripts/journalsunum_{manifestdogrula,gorseltara,paletdenetle,disaaktarimplanla,posteruret,pptxincele,yerlesimdenetle,destedogrula}.py`
  (CLIs) + `journalsunum_{ortak,manifestyukle,pptxokuyaz}.py` (libraries) +
  `generation_dependencies.json`.
- Plugin-root `scripts/office_kopru.py` — the Office bridge both render agents call (not
  owned by this skill; `journalstyle` and `journal-s-zotero` use its Word side).
- Provenance: adapted from `k-dense-ai/scientific-agent-skills` (`scientific-slides` 1.8,
  `pptx-posters` 2.2), MIT — headers in each file, licence in the root
  `THIRD_PARTY_NOTICES.md`.
