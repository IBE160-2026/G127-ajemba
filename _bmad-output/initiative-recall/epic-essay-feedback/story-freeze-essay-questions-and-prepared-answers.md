---
id: 1
type: story
title: "Freeze essay questions and prepared answers"
parent: epic-essay-feedback
covers: [FR-26, FR-29]
after: [6.1]
refined: true
hitl: true
risk: medium
---

# Freeze essay questions and prepared answers

## Description

**This is your work, not code.** For each test lecture you write 1-2 essay questions with at least three Reference Key Points each, and six prepared answers per question that you mark in advance with the key points they cover. Then everything is frozen before any AI feedback is judged. You commit the frozen files yourself.

## Acceptance Criteria

1. **Questions and key points exist first**
   **Given** each test lecture
   **When** you write the essay questions
   **Then** each question has at least three Reference Key Points with slide numbers, committed before any essay feedback from the AI is evaluated
2. **Six answers per question**
   **Given** each frozen question
   **When** you write the prepared answers
   **Then** there are two good answers (covering all or most key points), two weak answers (covering at most one), and two misunderstanding answers (covering fewer than the good ones, each with a typical wrong idea)
3. **Each answer is marked in advance**
   **Given** each prepared answer
   **When** it is saved
   **Then** the covered key points are listed next to it (by index) before any AI assessment
4. **Language-error check is possible**
   **Given** PRD open question 8
   **When** you write one good answer
   **Then** it contains deliberate spelling and grammar mistakes so a later check can show they do not lower the rating (offered as an assumption, below)
5. **Frozen files cannot change quietly**
   **Given** the essay files and their fingerprint
   **When** any of them changes
   **Then** a test fails naming the file
6. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** the "Test Set" section is extended with the frozen essay questions and the six prepared answers per question

## Tests

- `test_readme_has_required_sections` (list unchanged; "Test Set" already exists)
- `test_fr26_frozen_essay_files_match_fingerprint`
- `test_fr29_each_question_has_six_answers_in_three_groups`
- `test_fr29_each_question_has_at_least_three_key_points`
- `test_prepared_answers_have_marked_key_points`

## Boundaries

- Must not change: the frozen lecture key points from epic-evaluation story 1. No app code in this story.

## References

- parent — _bmad-output/initiative-recall/epic-essay-feedback/epic-essay-feedback.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-26, FR-29, open questions 7 and 8
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-13.5

## Notes

- Assumption: one question per lecture is enough (two lectures give two questions and 12 prepared answers) to save your time; confirm or raise to two per lecture.
- Assumption: one good answer with deliberate language errors is included to cover open question 8.
