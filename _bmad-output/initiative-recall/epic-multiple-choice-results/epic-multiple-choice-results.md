---
type: epic
title: "Multiple choice, results and saved lectures"
parent: initiative-recall
covers: [FR-12, FR-13, FR-18, FR-19, FR-20, SM-3, SM-6]
after: []
assignee: ""
risk: medium
---

# Multiple choice, results and saved lectures

## Description

A student opens the Multiple Choice quiz of a Ready Lecture, answers 10 questions with instant feedback, and sees a score and a Review List of topics to revisit. Questions are generated once and stored. This epic builds the quiz, scoring, results and Review List pattern that the other quiz types reuse, and completes the list of saved lectures with past attempts.

## Outcome

A student gets an exact score and a Review List linked to the right Summary Parts (SM-3, SM-6); saved lectures can be reopened without a new AI call.

## Done when

1. Ten Multiple Choice questions are generated once, each with four options, exactly one correct, a Summary Part link and a Source Reference (FR-12).
2. The score for a known set of answers is exact; skipped and unanswered questions count as wrong (FR-13).
3. The results page shows the score, the correct answers and the Review List with one entry per Summary Part and a message when nothing is wrong (FR-18, FR-19).
4. Quiz progress is kept on reload (AD-11).
5. The saved-lectures list shows only the user's lectures, with past attempts; opening one makes no AI call (FR-20).

## Boundaries

The quiz screens, scoring and Review List pure modules, quiz generation, results and the saved list. Not fill-in or essay questions (later epics); the code must leave room for them in the Question and Quiz tables.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-12, FR-13, FR-18, FR-19, FR-20, SM-3, SM-6
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-2, AD-5, AD-11, AD-17, AD-18, AD-22
- design — _bmad-output/initiative-recall/ux-recall/wireframes/02-my-lectures.md, 06-quiz-multiple-choice.md, 09-results.md

## Notes

- Decision: no extra design for the busy student; same flow (PRD §2.1).
- Decision: tracer bullet is story 2 (generate and answer one real quiz); story 1 (pure scoring) comes first so no wrong score can come from the model. Story 3 closes the flow.
- Tier: must-have.
