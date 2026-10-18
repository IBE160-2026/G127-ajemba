---
id: 2
type: story
title: "Multiple choice generation and quiz screen"
parent: epic-multiple-choice-results
covers: [FR-12, FR-13, SM-3]
after: [1, 3.3, 3.4]
refined: true
hitl: false
risk: high
---

# Multiple choice generation and quiz screen

## Description

When a student first opens the Multiple Choice quiz of a Ready lecture, the app generates 10 questions in a background job and stores them, so retakes use the same questions. The quiz screen shows one question at a time with four options, instant feedback after each answer, a Skip button, and progress saved on the server so a reload resumes where the student was. If one session is not enough, split this story into generation first and the screen second.

## Acceptance Criteria

1. **Questions are generated once**
   **Given** a Ready lecture with Summary Parts and a quiz in `not_made`
   **When** the student opens the quiz for the first time
   **Then** the quiz goes `not_made`, `making`, `ready`, `N_MC` (10) questions are stored, and opening it again or retaking makes no new AI call
2. **Each question is well formed**
   **Given** a generated question
   **When** it is validated
   **Then** it has exactly four options, exactly one correct option, a `part_id` that exists in the lecture, a valid Source Reference, and no `http`, `<`, `>` or `hx-`; a broken one is rejected and retried at most twice, then the quiz is `failed` with a retry button (up to 3 times)
3. **The prompt is versioned and plain**
   **Given** `prompts/questions.md`
   **When** it is read
   **Then** it has a version and changelog line, the plain-language instruction, no double negatives or idioms, and receives the stored Summary Parts with their ids
4. **One question at a time with instant feedback**
   **Given** an open quiz
   **When** the student picks an option
   **Then** the answer is saved on the server, the screen shows right or wrong with the correct option and its Source Reference, and the answer key is not in the page until the answer exists
5. **Skip works**
   **Given** an unanswered question
   **When** the student presses Skip question
   **Then** it is saved as skipped (counts as wrong in the score) and the next question appears
6. **An answer cannot change**
   **Given** an answered question
   **When** a second answer for it is posted
   **Then** the server refuses it and the stored answer stays
7. **Progress survives**
   **Given** an in-progress attempt at question 4
   **When** the page is reloaded or reopened later
   **Then** it resumes at question 4, and there is at most one in-progress attempt per user and quiz
8. **The AI notice and ownership hold**
   **Given** the quiz page
   **When** it loads
   **Then** it shows the AI-generated notice, and another user or a logged-out visitor gets the shared 404 or the login redirect
9. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Quizzes" section says that questions are made once and reused, that progress is saved, and how Skip works

## Tests

- `test_readme_has_required_sections` (adds "Quizzes" to the list)
- `test_fr12_each_question_has_four_options_one_correct`
- `test_fr12_questions_generated_once_and_reused`
- `test_sm2_question_links_to_existing_summary_part`
- `test_fr27_broken_question_response_rejected_and_retried`
- `test_fr13_answer_written_once`
- `test_progress_resumes_after_reload`
- `test_answer_key_not_in_page_before_answer`
- `test_quiz_pages_owner_only`

## Boundaries

- Must not change: the scoring and Review List modules from story 1 (use them, do not copy them); the Summary rows. Fill-in and essay quizzes are later epics.

## References

- parent — _bmad-output/initiative-recall/epic-multiple-choice-results/epic-multiple-choice-results.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-3.6, AD-5.1, AD-5.9, AD-11, AD-17, AD-18.3, AD-22
- design — _bmad-output/initiative-recall/ux-recall/wireframes/06-quiz-multiple-choice.md; EXPERIENCE.md (Interaction Primitives)
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-12, FR-13, SM-3

## Notes

- Handoff: progress is read and written through a `ProgressStore` interface with a database implementation, so epic-demo-readme story 1 only adds the session implementation.
- Generation time under 60 seconds is checked in the real evaluation run (epic-evaluation), not in a unit test.
- Assumption: a Quiz tab is added to the lecture page next to the Summary.
