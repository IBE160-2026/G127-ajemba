---
type: initiative
title: "Recall v1: lecture PDF to summary and self-test"
parent: none
covers: [FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-22, FR-23, FR-24, FR-25, FR-26, FR-27, FR-28, FR-29, FR-30, FR-31, SM-1, SM-2, SM-3, SM-4, SM-5, SM-6, SM-7, SM-8, SM-9, SM-10, SM-11]
assignee: ""
risk: medium
---

# Recall v1: lecture PDF to summary and self-test

## Description

Recall is a local web app that turns a lecture PDF into a plain-language summary and tests the student with multiple choice, fill-in-the-gaps and essay questions. Every summary part, question and piece of feedback points back to the slides it came from. The PRD owns the requirements; this initiative delivers them in ten epics, ordered so that a small, tested core with Demo Mode and a README exists first.

## Outcome

A second-language student can upload a text-based lecture PDF and learn in about fifteen minutes what they understood; the examiner can run the app from the README without any key, and the stored evaluation report shows how the AI's output was checked.

## Done when

1. The PRD success metrics SM-1 to SM-9 pass for every feature that is in the delivered cut (see Notes for the cut).
2. A fresh clone runs in Demo Mode from the README with no keys (SM-9).
3. The automated test suite passes with no API key and no `.env`, and each test names the FR or SM it verifies (PRD §6.5).
4. A stored evaluation report on 2 test lectures shows the checks that were run, and the README states what was checked and what was not (PRD §5.7).
5. Every epic that was not built is listed in Notes as dropped, with the reason.

## Boundaries

The whole of Recall v1 as one local Django web app, one background worker and one SQLite file (architecture AD-1). Not in v1: scanned PDFs, audio or video, shared quizzes, Canvas, mobile apps, payments, email verification, password reset, an admin screen (PRD §8.2). Tracer path across epics: log in, upload the real PowerPoint PDF, wait for the Summary, read it, take the multiple choice quiz, see results.

- Touch point: Google Gemini API — consumed only through `ai_client.py`; owner: epic-summary
- Touch point: pdfplumber — consumed only through `pdf_text.py`; owner: epic-upload-pdf-checks
- Touch point: django-q2 (or the thread fallback) — consumed only through `jobs.py`; owner: epic-summary

## References

- spec — _bmad-output/initiative-recall/prd-recall/prd-recall.md (FR and SM ids)
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md (AD-1 to AD-24; build order in AD-7 and AD-9)
- design — _bmad-output/initiative-recall/ux-recall/EXPERIENCE.md and DESIGN.md; wireframes in ux-recall/wireframes/
- constraint — _bmad-output/initiative-recall/architecture-recall/gemini-terms-checked-2026-10-17.md (upload notice wording)

## Notes

- Decision: deadline is the end of November 2026; the builder has about 30 hours for building and about 8 for the reflection report (user, 2026-10-18).
- Decision: epics 1 to 5 are the must-have core: accounts, upload, Summary, Multiple Choice with results, Demo Mode and README. Epic 6 (slim evaluation) is also must-have because the lecturer asked for a check of the AI's quality (user, 2026-10-18).
- Decision: "if time", in priority order after epic 6: 7 Fill-in-the-gaps, 8 Essay questions and feedback (also extends the evaluation to essays), 9 Delete a lecture and report a question, 10 Polish. If time runs out, drop from the bottom (user, 2026-10-18).
- Decision: slim evaluation covers Summary completeness and faithfulness and Multiple Choice grounding and answer keys on 2 test lectures, using the two-step report with the review sheet (user, 2026-10-18).
- Decision: two test lectures of about 10-12 slides each. Test lecture 1 is the builder's own slides on a topic they know well, made in PowerPoint and exported to PDF; it is also the FR-4 extraction test. Test lecture 2 is a freely licensed deck, for example from OpenStax, with the licence checked and credited in the repo. No course material from lecturers is used (user, 2026-10-18).
- Decision: stories are about 2 hours each and each ends in a working, committable state, because the builder's time comes in irregular blocks from shift work (user, 2026-10-18).
- Decision: the login-failure limit stays in story 1.2 (user, 2026-10-18).
- Decision: a checkpoint story (3.5) closes epic 3 and epic 4 waits on it: compare real hours with the plan and adjust the cut (user, 2026-10-18).
- Decision: no CI or deployment epic, because Recall v1 is local-only (architecture AD-15, PRD §8.2); epic 1 is the baseline and every epic's "production" is a local run from the README.
- Decision: no "Refactor sweep" closing story in any epic (user, 2026-10-18). There is also no closing end-to-end suite, because the PRD has no separate test plan for one; the per-story tests and the evaluation are the proof.
- Decision: the README is never at risk. It is started in story 1.1 with install and start commands, every later story adds its own README section (checked by one test that lists the required headings), and story 5.2 is only the final check and polish from a fresh clone (user, 2026-10-18).
- Planning figures (not estimates stored on stories), recalculated 2026-10-18 after the README change: epic 1 about 5.8 hours, epic 2 about 6, epic 3 about 8.1, epic 4 about 6, epic 5 about 3, epic 6 about 6, so the must-have core is about 35 hours against about 30 available. Story 1.1 grew by about 0.5 hour and every other story by about 10 minutes for its README part; story 5.2 shrank by about 45 minutes. Story 6.3 (the real evaluation run) and story 5.2 are the first at risk, and the checkpoint after epic 3 is where this is re-checked. The if-time epics add about 15 more.
- Assumption: the hour estimates in the plan are rough guesses and are checked again after epic 3.
- Assumption: the Example Lecture data grows as epics land. Epics 7 and 8 must add their quiz content to it, because Demo Mode (FR-23) promises all three quizzes.
- Open question: definition of "unsupported statement" for faithfulness (PRD open question 6); epic-evaluation waits on it.
- Waits: see `tickets.toml` for what each epic needs from the earlier ones.
