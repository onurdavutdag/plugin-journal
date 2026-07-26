# Reporting Guidelines — Item-Level Package

This directory holds the **item-level, IMRaD-section-grouped, distilled** summaries of the EQUATOR Network
(www.equator-network.org) reporting guidelines. After the `journalwriter-s-danisman` agent determines the study
type, it **Reads the matching file** and folds the relevant items for that section into the writing guidance.

`journalwriter-s-danisman-r-bilgi.md` §5 only **names** the guidelines; the item content is here.

## Study type → guideline file

| Study type | Guideline | File | Source |
|---|---|---|---|
| Randomized controlled trial (RCT) | CONSORT | `CONSORT.md` | official checklist (CONSORT 2010, BMJ) |
| Observational (cohort / case-control / cross-sectional) | STROBE | `STROBE.md` | official checklist (STROBE v4, 3 variants) |
| Systematic review & meta-analysis | PRISMA | `PRISMA.md` | memory (verify with EQUATOR) |
| Case report / case series | CARE | `CARE.md` | official checklist (CARE 2013) + 2 Turkish editor guides |
| Diagnostic accuracy study | STARD | `STARD.md` | official checklist (STARD 2015) |
| Prognostic / prediction model | TRIPOD | short note inside `STARD.md` | memory (verify with EQUATOR) |
| Experimental animal study | ARRIVE | `ARRIVE.md` | memory (verify with EQUATOR) |

**Source column:** `official checklist` = derived one-to-one from the official checklist of the relevant EQUATOR
guideline; `memory` = a distilled summary — verify with the official EQUATOR checklist before submission.

## Rules

- **Do not fabricate a guideline not in the files.** Tell the user "the item detail of this guideline is not
  in the package"; make do with the general `bilgi.md` §5 mapping or ask the user for a source.
- These summaries are **not official copies** of the guidelines; they are application notes distilled in our own
  words. A final check with the official checklist (EQUATOR) before submission is recommended.
- The item numbers are aligned with the official guideline's numbering so the author can match them while filling
  in the checklist.
