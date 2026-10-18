---
id: 1
type: story
title: "Scoring and Review List as pure code"
parent: epic-multiple-choice-results
covers: [FR-13, FR-19, SM-3, SM-6]
after: [3.5]
refined: true
hitl: false
risk: high
---

# Scoring and Review List as pure code

## Description

Scoring and the Review List are written first as plain Python with no database, no request and no AI, so a wrong score can never be caused by a model. Each has exactly one entry function, and both work on the frozen dataclasses in `core/types.py`. The same modules are reused for fill-in and essay questions later.

## Acceptance Criteria

1. **Shared shapes exist**
   **Given** `core/types.py`, which already holds `SourceRef` from epic-summary story 3
   **When** it is imported
   **Then** it also holds the frozen dataclasses `AnswerRecord`, `QuestionRecord` and `AttemptResult`, and a question has a kind (`mc`, `fill`, `essay`) so later quiz types fit
2. **The score is exact**
   **Given** 10 questions and 7 correct answers
   **When** `score(questions, answers)` runs
   **Then** the result says 7 of 10, and the denominator is the number of questions in the quiz, never the number of answers given
3. **Skipped and missing count as wrong**
   **Given** 3 correct, 2 skipped and 5 never visited out of 10
   **When** it is scored
   **Then** the score is 3 of 10
4. **The Review List groups by Summary Part**
   **Given** wrong or skipped answers on questions from parts A, A and B
   **When** `build_review_list(...)` runs
   **Then** there are two entries, one for A and one for B, each with the part's Source Reference, in a stable order
5. **No wrong answers means an empty list**
   **Given** all answers correct
   **When** the Review List is built
   **Then** the list is empty (the screen shows a message in story 3)
6. **The modules are pure**
   **Given** `scoring.py` and `review_list.py`
   **When** the import-boundary test runs
   **Then** they import no models, no request and no network, and no view or service computes a score by itself
7. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a short "Scoring" section says how the score and the Review List are worked out (skipped counts as wrong, one entry per Summary Part)

## Tests

- `test_readme_has_required_sections` (adds "Scoring" to the list)
- `test_sm3_score_seven_of_ten`
- `test_fr13_skipped_and_unvisited_count_as_wrong`
- `test_sm6_review_list_one_entry_per_summary_part`
- `test_fr19_skipped_question_creates_entry`
- `test_fr19_no_wrong_answers_gives_empty_list`
- `test_ad2_pure_modules_have_no_forbidden_imports`

## Boundaries

- Must not change: tables and views from earlier epics. No quiz screens here. Essay rules (last submission counts) are added in epic-essay-feedback.

## References

- parent — _bmad-output/initiative-recall/epic-multiple-choice-results/epic-multiple-choice-results.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-2.2–2.3, AD-21.3
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-13, FR-19, SM-3, SM-6

## Notes

- This story waits on the epic-3 checkpoint so the cut is checked before the quiz work starts.
