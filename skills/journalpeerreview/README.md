<!-- Oluşturma: 20260725 0056 -->
# journalpeerreview — skill README

Evaluates a manuscript **before submission** the way a journal reviewer would: methodology,
statistics, study design, reproducibility, ethics, figure/data integrity, reporting-standard
compliance. Advisory only — it never edits the manuscript.

## When it triggers

Turkish trigger phrases (from the SKILL.md `description`): *"hakem değerlendirmesi yap"*,
*"makaleyi/taslağı hakem gözüyle eleştir"*, *"reviewer gözünden bak"*, *"gönderim öncesi eleştirel
değerlendirme"*, *"peer review yap"*, *"reviewer 2 gibi bak"*, *"bu makale yayına hazır mı"*.

## Input / output

- **Input:** the manuscript (`.docx` / `.pdf` / `.md`) + target journal (optional) + study type.
- **Output:** a separate report file `<name> YYYYMMDD HHMM.md` — summary evaluation with a decision
  recommendation (accept / minor / major / reject), numbered major and minor comments, optional
  line-based comments, questions to the author. Opens with the mandatory provenance block.
- **Language:** matches the manuscript's language.

## Subagents

**None.** The skill runs the 7-stage review itself and borrows other skills' reference material
read-only.

## Handoff table — the reviewer diagnoses, others fix

| Finding | Handed to |
|---|---|
| Unsupported / missing / weak citation | `journalresearch` (finds the source) + `journalwriter` (works it in) |
| Citation or bibliography format, numbering, style | `journal-s-zotero` (agent) |
| Mechanical format, section order, word limit | `journalstyle` |
| Section structure or writing weakness | `journalwriter` |
| Analysis/statistics need redoing | the user / the global `istatistik-profesoru` skill |

## Constraints

- **Never touches the manuscript file.** `Write` permission exists only to create the report.
- No fabricated findings: every point rests on what is actually in the text. Anything uncertain goes
  under "questions to the author", not under major comments.
- Calibrates to the workspace `authorguidelines/<slug>.json` + `yayinstili/<slug>.yayinstili.json` when present;
  otherwise states in the report that general standards were used. Never invents a journal rule.
- Audits against the user's global number/p-value format and statistical-test symbol standards.

## Files

- `SKILL.md` — the 7-stage flow and report structure.
- `references/journalpeerreview-r-common-issues.md` — 22 recurring methodology/statistics errors:
  definition, how to detect, what to suggest.
- Reused read-only (owned by `journalwriter`): `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalwriter/references/journalwriter-s-danisman-r-guidelines/`
  (CONSORT · STROBE · PRISMA · CARE · STARD · ARRIVE).
