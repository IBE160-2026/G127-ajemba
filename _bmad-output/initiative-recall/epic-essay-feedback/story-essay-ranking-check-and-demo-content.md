---
id: 4
type: story
title: "Essay ranking check and demo content"
parent: epic-essay-feedback
covers: [FR-29, SM-5, FR-23]
after: [1, 3, 6.3, 5.1]
refined: true
hitl: true
risk: high
---

# Essay ranking check and demo content

## Description

The evaluation is extended to prove the essay feedback is trustworthy: each prepared answer is assessed three times, and good answers must rank above weak and misunderstanding answers every time. Demo Mode gets prepared essay answers with stored feedback. **Your part (hitl):** run the real evaluation, fill in the review sheet, and review the demo feedback. A failure is a finding that leads to a prompt change, not a hidden result.

## Acceptance Criteria

1. **Each prepared answer is assessed three times**
   **Given** the frozen essay questions and six answers each
   **When** `evaluate` runs
   **Then** each answer goes through the Essay Feedback step three times, and the AI-generated essay questions from story 2 are generated too and checked for grounding but not used for the ranking
2. **Good ranks above weak and misunderstanding**
   **Given** the ratings of one run
   **When** the ranking check runs
   **Then** every good answer has a higher rating than every weak answer and every misunderstanding answer, and the check passes only if this holds in all three runs
3. **Feedback names the right gaps**
   **Given** each weak and misunderstanding answer
   **When** the feedback is read
   **Then** it names at least one missing key point matching a Reference Key Point, and the misunderstanding feedback names the missing or wrong point
4. **The deliberate language errors do not lower the rating**
   **Given** the good answer with spelling and grammar mistakes
   **When** it is rated
   **Then** its rating is not lower than the other good answer for the same question
5. **Failures are recorded**
   **Given** a failed check
   **When** the report is written
   **Then** it appears as a finding and the report is stored, a prompt change follows the epic-evaluation rules, and it is re-run after the change
6. **Demo Mode shows prepared answers**
   **Given** the Example Lecture
   **When** a visitor opens the Essay quiz
   **Then** they can select and submit prepared example answers and see stored feedback from a reviewed real run, free-text answers say they need an API key, and no AI call is made
7. **The README is updated**
   **Given** the evaluation result
   **When** it is stored
   **Then** the README "what we checked and what we did not" section reflects the essay result
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** the "What we checked and what we did not" and "Demo Mode" sections are updated with the essay ranking result and the prepared demo answers

## Tests

- `test_readme_has_required_sections` (list unchanged; both headings already exist)
- `test_sm5_ranking_logic_on_replay_data` (good above weak above, all three runs)
- `test_fr29_every_prepared_answer_assessed_three_times`
- `test_fr23_demo_essay_uses_stored_feedback_without_ai`
- `test_demo_free_text_essay_shows_needs_key_message`
- Manual by you: real run, review sheet and stored report

## Boundaries

- Must not change: frozen test files, other quiz types.

## References

- parent — _bmad-output/initiative-recall/epic-essay-feedback/epic-essay-feedback.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-10.7, AD-13
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-29, SM-5, FR-23

## Notes

- Open question: how to compare the AI's covered points with your marked points (PRD open question 7); default is exact index match, with mismatches listed for you to judge.
