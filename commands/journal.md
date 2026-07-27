---
description: Makale işini çözümle ve doğru journal bileşenine yönlendir
argument-hint: "[istek] — ör. tartışmayı yaz, dergi Spine (boş bırakılabilir)"
---

User's request: $ARGUMENTS

Act as the single entry point of the `journal` plugin: read the request, decide which skill or agent owns the job, collect the information that owner requires, and hand the job
over. Do the work of routing only — never perform the owner's job inside this command.

## 1. No arguments given

If `$ARGUMENTS` is empty, ask with `AskUserQuestion` what the job is. Offer these options:

- **Bölüm yaz** — write a manuscript section (Introduction/Methods/Results/Discussion/Abstract/Conclusion)
- **Kaynak bul / doğrula** — find or verify real DOI/PMID references for a claim
- **Word'e atıf + kaynakça** — write in-text citations and a bibliography into a `.docx`
- **Dergiye biçimle** — format a `.docx` to the target journal's author guidelines

If none fits, the user picks "Other" and describes the job in free text; treat that text as the
request and continue with section 2. When the free-text answer is a peer review ("hakem gözüyle
eleştir", "yayına hazır mı"), a NotebookLM job, or a full pipeline run ("baştan sona hazırla"), route
it exactly as section 2 and 3 prescribe.

Then collect the required information for the chosen owner (the "Required information" column below).
Ask only for what is genuinely missing — a `.docx` already named in the conversation, or a journal
already agreed on, is not asked again.

## 2. Intent → owner mapping

Match the request against this table. It mirrors `CLAUDE.md` §3 (trigger table) and §7
(single-ownership) — do not invent a different split.

| Intent in the request | Owner | Required information |
|---|---|---|
| write a section: intro / methods / results / discussion / abstract / conclusion, "makale metni oluştur" | skill **`journal:journalwriter`** | target journal + article type + source file + language (+ which section; if unstated, all) |
| find sources, verify a claim, PubMed, Consensus, "PDF'lerimde ara", "bu cümleye kaynak" | skill **`journal:journalresearch`** | the claim/sentence or the topic |
| Zotero library, add by DOI/PMID, write bibliography into Word, change citation style — a FILE is processed | agent **`journal:journal-s-zotero`** (Task) | the `.docx` + (to add) DOI/PMID **or** the desired citation style |
| format for a journal, prepare for submission, match the template, apply author guidelines | skill **`journal:journalstyle`** | the `.docx` + target journal name (+ article type) |
| peer review, critique as a reviewer, "yayına hazır mı", pre-submission critique | skill **`journal:journalpeerreview`** | the manuscript (`.docx`/`.pdf`/`.md`) (+ journal, study type — optional) |
| NotebookLM: query a notebook, audio overview, infographic, mind map, deep research, source curation | agent **`journal:journal-s-notebooklm`** (Task) | which notebook + the desired output |
| statistics/analysis: t-test, ANOVA, correlation, regression, "istatistik profesörü" | **outside this plugin** — point at the global `istatistik-profesoru` skill and say so plainly | the dataset |

Open the owner with the `Skill` tool (agents with `Task`), passing the user's intent plus everything
collected. Two of the seven owners are agents — zotero has no skill of its own any more. State in one line which owner was chosen and why, then hand over.

**Teaching the Zotero GUI is out of scope since 1.9.0.** "Zotero nasıl kullanılır", "ISBN ile kitap
ekle", "Isnat 2 stili", "DİA maddesi" and the like have **no owner** in this plugin — say so in one
line and stop. Do not route them to `journal-s-zotero`, whose job is the file, not the lesson.

When two owners fit (e.g. "kaynakça bas ve dergiye biçimle"), run them in the section 3 order rather
than picking one.

## 3. Full pipeline mode

Triggers: "baştan sona hazırla", "submission'a kadar götür", "her şeyi yap".

Run the submission-ready order from `CLAUDE.md` §7:

1. `journal:journalwriter` — write the text
2. `journal:journal-s-zotero` (agent) — citations + bibliography into the docx
3. `journal:journalstyle` — mechanical formatting for the journal
4. `journal:journalpeerreview` — reviewer critique before submission

Summarise each step's output and **get the user's approval before starting the next one**. Never
chain all four silently.

## 4. Limits

- This command writes no manuscript text, formats no file, prints no citation, produces no review —
  every one of those belongs to its owning skill.
- Do not call the plugin's sub-agents on the user's behalf; the skills call their own. The two
  exceptions `CLAUDE.md` §5 lists as directly callable are `journal-s-notebooklm` and
  `journal-s-zotero` — the latter because it has no owning skill any more, so the command reaches
  it directly.
- The red lines in `CLAUDE.md` §9 hold: no fabricated source or citation, docx citation/bibliography
  is `journal-s-zotero`'s authority alone, and no verbatim sentence is copied from a publisher PDF.
- If the request is not a journal-plugin job at all, say so in one line and stop — do not force a
  skill onto it.
