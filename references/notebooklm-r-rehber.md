<!-- Oluşturma: 20260725 1312 -->
# notebooklm-r-rehber — distilled NotebookLM knowledge

The single persistent knowledge source for the `journal-s-notebooklm` agent. Distilled from the user's
own curated video/course material on NotebookLM (six sources; the originals are not stored here — only
rules, numbers and structure, no verbatim passages).

Body is English (plugin convention); example prompt strings stay Turkish because that is the language
the user types.

---

## 1. What NotebookLM is

A **grounded (closed-circuit)** research assistant: it answers from the sources *you* uploaded, not from
the open web. Two consequences that shape every decision below:

- **Low hallucination risk by construction.** Each answer carries clickable citations pointing at the
  exact passage in the source, so any claim can be traced back.
- **The grounding breaks the moment you ask it to leave the sources.** A prompt like "kaynaklarda yoksa
  kendi bilginden tamamla" switches it to the underlying general model, and normal hallucination risk
  returns. Never ask for that.

If the user has **no sources yet**, NotebookLM can gather them itself — **Deep Research** (Derin
Araştırma) sweeps the web for high-quality, peer-reviewed, open-access material and imports it; the
lighter **Discover sources** (Kaynak Keşfet) mode pulls from general platforms.

## 2. Source types

PDF · web page URL · YouTube link (**transcript only**) · audio files · pasted text · Google Drive
documents · images (PNG/JPG). Mixing modalities on one topic is encouraged — a multimodal library
answers better than a PDF-only one.

## 3. Studio outputs

| Output | What it produces |
|---|---|
| **Audio Overview** (Sesli Özet) | Two AI hosts discussing the sources, podcast style; downloadable as MP3. In **English** the user can interrupt and ask questions live. |
| **Video Overview** | ~5-minute narrated slide walkthrough. |
| **Mind Map** | Hierarchical concept graph; nodes are clickable into a chat query on that node. |
| **Flashcards** | Q/A cards with an "Explain" action for the ones that don't land. |
| **Quiz** | Multiple choice; explains *why* a wrong answer is wrong, from the sources, and offers hints. |
| **Study guide** | Key-concept glossary + short-answer questions. |
| **Reports** | Blog post, briefing doc, technical/policy report. |
| **Data table** | Comparative table of key values across sources. |
| **Infographic** | One-page schematic summary; works as a graphical abstract or poster. Horizontal/vertical/square, short→detailed. |

## 4. Quotas and limits

Numbers **as reported by the source material** — Google changes these; verify in-app before relying on
one, and never quote them to the user as current fact:

- Free tier: ~100 notebooks; **50 sources per notebook**. Pro: **300 sources per notebook**.
- Per document: **200 MB or 500,000 words**.
- Chat customization (system prompt): **10,000 characters** (raised from 500).

## 5. Failure modes

- **YouTube is read as transcript, not video.** Anything only shown on screen (whiteboard, chart,
  on-screen text) is invisible to it.
- **Paywalled, login-gated or encrypted pages** often cannot be imported. Broken or very old PDFs get
  rejected outright.
- **Very large documents** (tens of thousands of pages) lose detail; segment them instead.
- **Studio visuals** (infographic, slides) sometimes contain letter errors, run-together words, or a
  layout too dense to read when the source text is heavy. Final proofing belongs to the user.
- **Language leakage:** with Turkish instructions, headings or captions in visual outputs sometimes come
  back in English.
- **Interpretation drift in audio:** podcast generation occasionally invents an illustrative example that
  is not in the sources (e.g. describing a cohort study while explaining a case-control design).

## 6. Prompt patterns

1. **Persona.** Set the level explicitly: *"Bir doktora öğrencisi gibi akademik derinlikle anlat"* /
   *"Bir ortaokul öğrencisinin anlayacağı kadar sadeleştir"*. Useful personas: scientific researcher,
   teacher, product manager, critical peer reviewer.
2. **Scope limits.** Narrow the context deliberately: *"Yalnızca X kaynağını kullan"*, *"Sadece
   metodoloji kısmına odaklan"*, *"397-447. sayfalar arasını analiz et"*, *"Önceki yanıttaki tekrarlara
   düşme"*.
3. **Format.** State the shape: table, list, manuscript introduction paragraph, blog post, and if
   citations are wanted, *"sayfa numarası belirterek"*.
4. **Metaphor.** For equations and dense abstractions: *"Bunu bir metaforla açıkla"*. Pair with Mind Map
   when the difficulty is structural rather than conceptual.
5. **Stepwise iteration.** Broad summary first, then narrow: save the good answer as a note, **convert
   the note to a source**, and query on top of that refined layer.
6. **System prompt (10k chars).** Put the standing rules there — tone, never skip references, output
   skeleton — plus a few sample outputs (few-shot) so it copies the user's style. It affects chat, audio
   overviews and quizzes alike.

## 7. Source management

- **Curate, don't dump.** Prefer peer-reviewed, high-impact material; garbage in, garbage out. Review
  what Deep Research imported and drop the weak or off-topic items.
- **One notebook per topic.** Keeps context from bleeding across projects.
- **Segment long works.** Upload a book chapter by chapter so queries can target a chapter sharply.
- **Clean up.** Remove sources that failed to import (red warning), dead URLs, paywalled links and
  broken PDFs — they degrade answers.
- **Feedback loop.** Valuable chat syntheses: save to note → convert to source. The refined output then
  becomes part of what later queries stand on. Note: this is retrieval (RAG), **not model training** —
  the sources' word "eğitmek" is a metaphor, do not repeat it as a technical claim.

## 8. Decision rules — goal → tool

| Goal | Use |
|---|---|
| Understand a hard concept, equation or process | metaphor prompt; Mind Map if the structure is the problem |
| Build a presentation or poster | slide deck / Infographic (graphical abstract) |
| Consolidate and self-test | Flashcards + Quiz + study guide |
| Learn while commuting or working | Audio Overview, download MP3 |
| No sources yet | Deep Research (or Discover sources) |
| Find the literature gap | Deep Research first, then a gap-analysis prompt |
| Locate one clause in a huge manual/legal text | upload the PDFs, ask the case directly, demand page references |

Worked gap-analysis prompt: *"Yalnızca sağlanan kaynaklara dayanarak, bu konudaki kanıtların eksik veya
çelişkili olduğu 3 temel noktayı referanslarıyla belirle ve bu boşlukların neden bilimsel bir proje
konusu olabileceğini açıkla."*

## 9. Red lines

- **NotebookLM output is a draft, never final manuscript text.** Pasting it into a thesis or paper
  carries plagiarism risk; the user rewrites it in their own voice.
- **Assistant, not authority.** Every reference it gives gets clicked and checked. It does not settle
  questions of fact or belief.
- **In this plugin, a NotebookLM answer is content, never a citation.** Every study it points to must be
  verified through the `journalresearch` skill with a real DOI/PMID before a `{{zref:KEY}}` is written.
- **Never state a price or subscription tier as fact** (see below).

## 10. Conflicts and open questions

Recorded openly, because the plugin's rule is: uncertain → do not fabricate, tell the user.

- **Pricing conflicts across the sources** — monthly figures of ~100, ~200 and ~800 TL all appear, plus a
  claim that a `.edu` address gets Pro free for a year. Do not repeat any of these as current; tell the
  user to check in-app.
- **Deep Research reach** is unclear — it is described as focused on open-access material; how far it
  gets behind paywalls is not established.
- **Turkish interactive audio** — the live "raise hand" interruption is documented for English; its
  Turkish performance is unverified.
- **Video Overview depth** — how far beyond static narrated slides it goes (real animation) is not fixed.
- **"Training" wording** — sources say the AI is being "trained"; technically it is retrieval-augmented
  generation over the uploaded sources.

## 11. Call procedure

This procedure is the **single** source for both callers (`journalwriter` §3d, `journalresearch` Step 1b).
Neither SKILL.md repeats it; they point here. The agent itself reads §1–10 above; this section is written
for the callers.

**1. When to call at all.**
- `journalwriter`: **only** for the **Introduction** and the **Discussion**. Writing Methods, Results,
  Abstract or Conclusion, do not call the agent — there is no background/comparison layer to fetch.
- `journalresearch`: only as **tier 3**, after the user's own supplied references (tier 1) and the
  uploaded PDFs including `pdflerim/` (tier 2) failed to support the claim.
- Never call the MCP tools directly. Every `mcp__notebooklm-mcp__*` call in this plugin belongs to
  `journal-s-notebooklm`; call it with the `Task` tool, automatically, without waiting for approval.

**2. The brief to pass.** The scenario (Introduction · Discussion · claim verification) · the
manuscript's topic and, for a Discussion, its main findings · the notebook name if the user gave one ·
the output needed. The agent owns the query shapes — do not hand it a prompt to run.

**3. What comes back.** The structure defined in the agent's **"Output Format"**: findings tied to their
notebook and sources, a separate `Claims to verify` list, skipped steps, and warnings. What the caller
does with it differs: `journalwriter` uses the findings as raw material for the **prose**;
`journalresearch` treats `Claims to verify` as its **verification queue** and proposes only what PubMed
then confirms — it writes no prose.

**4. The two rules that bind the caller.**
- **Content, never a citation.** Every study in `Claims to verify` goes through `journalresearch` for a
  real DOI/PMID before a `{{zref:KEY}}` is written. A NotebookLM finding never becomes a citation
  directly.
- **Silent skip.** If the agent reports the MCP server unreachable or the session expired (it will
  suggest `nlm login`), skip this step and continue — the calling flow must not break. NotebookLM has no
  official API; the server runs over a browser session and breaks temporarily when Google changes
  something. Do not run `nlm login` on the user's behalf; it needs a browser.
