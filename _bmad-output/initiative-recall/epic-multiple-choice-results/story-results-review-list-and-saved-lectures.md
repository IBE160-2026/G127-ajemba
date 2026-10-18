---
id: 3
type: story
title: "Results, Review List and saved lectures"
parent: epic-multiple-choice-results
covers: [FR-18, FR-19, FR-20, SM-6]
after: [2]
refined: true
hitl: false
risk: medium
---

# Results, Review List and saved lectures

## Description

After the last question the student sees the score, each answer with the correct one, and a Review List of topics to revisit, each linked back to its Summary Part. The My lectures page is completed so a student can reopen any saved lecture, read its stored Summary, and see past attempts, without a new AI call.

## Acceptance Criteria

1. **The score is shown correctly**
   **Given** a finished attempt with 7 correct answers out of 10
   **When** the results page opens
   **Then** it shows "7 of 10", and for each question whether it was right, the student's answer, the correct answer and its Source Reference
2. **The Review List links back**
   **Given** wrong or skipped answers
   **When** the results page opens
   **Then** each entry links to its Summary Part on the Summary page and shows its Source Reference, and several wrong answers on one part give one entry
3. **Nothing wrong gives a message**
   **Given** an attempt with no wrong answers
   **When** the results page opens
   **Then** a message is shown instead of an empty list
4. **Start again**
   **Given** the results page
   **When** the student presses Start again
   **Then** the open attempt is finished and a new attempt starts with progress reset
5. **Saved lectures open without AI**
   **Given** a Ready lecture with past attempts
   **When** the owner opens it from My lectures
   **Then** the stored Summary appears, past attempts are listed with date, quiz and score, and a test that makes `ai_client` raise on any call still passes
6. **The list is private**
   **Given** two users with lectures
   **When** each opens My lectures
   **Then** each sees only their own, and requesting the other's attempt or results address gives the shared 404
7. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Results and saved lectures" section says how to read the results and the Review List and how to reopen a saved lecture

## Tests

- `test_readme_has_required_sections` (adds "Results and saved lectures" to the list)
- `test_fr18_results_score_matches_correct_answers`
- `test_fr19_review_entry_links_to_summary_part_with_source_ref`
- `test_fr19_message_when_no_wrong_answers`
- `test_fr20_open_saved_lecture_makes_no_ai_call`
- `test_fr20_list_shows_only_own_lectures`
- `test_sm6_every_wrong_answer_leads_to_review_entry`
- generated URL-by-user test from epic 1 still passes with the new addresses

## Boundaries

- Must not change: scoring and Review List code; answers are never edited. Fill-in and essay results are added in later epics.

## References

- parent — _bmad-output/initiative-recall/epic-multiple-choice-results/epic-multiple-choice-results.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-2, AD-8, AD-18.5, AD-22
- design — _bmad-output/initiative-recall/ux-recall/wireframes/02-my-lectures.md and 09-results.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-18, FR-19, FR-20, SM-6

## Notes

- This story completes the first full flow for the tracer path: upload, Summary, quiz, results.
