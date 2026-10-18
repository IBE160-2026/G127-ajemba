---
id: 2
type: story
title: "Fill-in generation, quiz screen, evaluation and demo content"
parent: epic-fill-in-gaps
covers: [FR-14, FR-15, FR-23]
after: [1, 4.2, 6.2, 5.1]
refined: true
hitl: true
risk: medium
---

# Fill-in generation, quiz screen, evaluation and demo content

## Description

The student takes a Fill-in-the-Gaps quiz of 8 questions, each a sentence from the lecture with one key term missing, and types the term. Questions are generated once and stored, the screen reuses the Multiple Choice pattern, and scoring and the Review List are the existing code. The evaluation gains a fill-in answer-key check and the Example Lecture gains fill-in content. **Your part (hitl):** re-run the evaluation after the prompt change and review the new demo content.

## Acceptance Criteria

1. **Questions are generated once**
   **Given** a Ready lecture
   **When** the student first opens the Fill-in quiz
   **Then** `N_FILL` (8) questions are stored, each with exactly one expected term that appears in the lecture text, a blank marker in its sentence, a Summary Part link and a valid Source Reference, and reopening makes no new AI call
2. **Bad output is rejected**
   **Given** a question with no blank, two expected terms, a term not in the text, or markup characters
   **When** it is validated
   **Then** it is rejected and retried at most twice, then the quiz is `failed` with a retry button
3. **Typing and feedback**
   **Given** the quiz screen
   **When** the student types an answer and presses Check
   **Then** the matching rules from story 1 decide, feedback shows with the expected term and Source Reference, and the answer is written once
4. **Skip works**
   **Given** a question
   **When** the student presses Skip question
   **Then** it counts as wrong and creates a Review List entry like a wrong answer
5. **Results reuse the existing code**
   **Given** a finished Fill-in attempt
   **When** results open
   **Then** score and Review List come from `scoring` and `review_list` with no second copy of the rules
6. **The evaluation checks answer keys**
   **Given** the Test Set lectures
   **When** the evaluation runs
   **Then** the report has a Fill-in answer-key section and review-sheet boxes, and the prompt version in `questions.md` is raised with a changelog line naming the report it was checked with
7. **Demo Mode offers the quiz**
   **Given** the Example Lecture
   **When** a visitor opens it
   **Then** the Fill-in quiz uses stored questions from a reviewed real run and no AI call
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** the "Demo Mode" and "What we checked and what we did not" sections are updated to include the fill-in quiz

## Tests

- `test_readme_has_required_sections` (list unchanged; both headings already exist)
- `test_fr14_fill_in_question_has_one_expected_term_in_text`
- `test_fr27_broken_fill_in_response_rejected`
- `test_fr15_skip_creates_review_entry`
- `test_fr23_demo_lecture_offers_fill_in_quiz`
- `test_fill_in_results_use_shared_scoring`
- Manual by you: evaluation re-run and report stored (FR-30)

## Boundaries

- Must not change: Multiple Choice behaviour and the matching rules. Question counts are settings.

## References

- parent — _bmad-output/initiative-recall/epic-fill-in-gaps/epic-fill-in-gaps.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-5, AD-6, AD-13, AD-17
- design — _bmad-output/initiative-recall/ux-recall/wireframes/07-quiz-fill-in-the-gaps.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-14, FR-15, FR-23

## Notes

- If one session is not enough, split demo content from generation and screen.
