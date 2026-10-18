---
id: 2
type: story
title: "Essay generation and feedback job"
parent: epic-essay-feedback
covers: [FR-16, FR-17]
after: [4.2, 7.2]
refined: true
hitl: false
risk: high
---

# Essay generation and feedback job

## Description

The app generates 2 essay questions per lecture, each with at least three Reference Key Points, and assesses a student's written answer in a background job. The model returns which key points the answer covers; the Essay Rating is then computed from those indices by one pure function and never stored. Feedback is about content, never spelling or grammar. The evaluation re-run for the prompt changes is done in story 4.

## Acceptance Criteria

1. **Essay questions are generated once**
   **Given** a Ready lecture
   **When** the student first opens the Essay quiz
   **Then** `N_ESSAY` (2) questions are stored, each with at least three Reference Key Points with valid Source References and a link to an existing Summary Part
2. **The feedback prompt is versioned and clear about language**
   **Given** `prompts/essay_feedback.md`
   **When** it is read
   **Then** it has a version and changelog, the plain-language instruction, and an instruction not to criticise or penalise spelling or grammar, and treats the student's answer as data
3. **The answer is bounded and protected**
   **Given** an answer of more than `ESSAY_MAX_CHARS` (3000)
   **When** it is submitted
   **Then** it is refused with a clear message, and `<<` and `>>` in any answer are neutralised before sending
4. **Covered key points come back as indices**
   **Given** an AI response
   **When** it is validated
   **Then** indices outside the key-point range are rejected, markup characters are rejected, and the feedback must say what is right, which key points are missing and which Summary Part to revisit, each with a Source Reference
5. **The rating is computed, not stored**
   **Given** the covered indices
   **When** the rating is needed
   **Then** one pure function returns the count of covered key points out of the total, and no rating column exists
6. **Empty answers get the lowest rating without an error**
   **Given** an empty or one-word answer
   **When** it is submitted
   **Then** the rating is 0, all key points are listed as missing, the student sees this feedback and not an error page, and no AI call is made
7. **Feedback is a queued job**
   **Given** a submission
   **When** it is created
   **Then** its status goes `queued` to `done` or `failed`, a failed submission shows a message and a retry, and the job drops its output if the row is gone
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** an "Essay feedback" section says feedback is about content, not spelling or grammar, and that empty answers get the lowest rating

## Tests

- `test_readme_has_required_sections` (adds "Essay feedback" to the list)
- `test_fr16_each_essay_has_at_least_three_key_points`
- `test_fr17_out_of_range_indices_rejected`
- `test_fr17_empty_answer_gets_lowest_rating_without_ai_call`
- `test_fr17_prompt_says_not_to_penalise_language_errors`
- `test_essay_rating_pure_function_counts_indices`
- `test_essay_answer_over_3000_chars_refused`

## Boundaries

- Must not change: Multiple Choice and Fill-in code; the pure scoring modules except to call the rating function.

## References

- parent — _bmad-output/initiative-recall/epic-essay-feedback/epic-essay-feedback.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-3.6, AD-5.2–5.8, AD-6, AD-17, AD-18.4
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-16, FR-17

## Notes

- Assumption: the "empty or one-word" rule is handled in code with no AI call, to save cost and make the result certain.
