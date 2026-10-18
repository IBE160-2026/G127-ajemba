---
type: epic
title: "Essay questions and feedback"
parent: initiative-recall
covers: [FR-16, FR-17, FR-18, FR-19, FR-23, FR-26, FR-29, SM-5]
after: []
assignee: ""
risk: high
---

# Essay questions and feedback

## Description

A student answers two essay questions in their own words and gets written feedback on content, not language: what was right, which key points are missing and which Summary Part to revisit. Up to three submissions are allowed per essay, the last one counts. The evaluation is extended to check that good answers rank above weak ones, three runs each, and Demo Mode gets prepared example answers.

## Outcome

On the Test Set every good answer is rated above every weak answer and every misunderstanding answer, in all three runs (SM-5).

## Done when

1. Two essay questions with at least three Reference Key Points each are generated and stored (FR-16).
2. Feedback names what is right, the missing key points and the Summary Part; empty or one-word answers get the lowest rating; language errors do not lower the rating (FR-17).
3. A fourth submission is refused; all submissions stay visible; the last counts for the rating and Review List (FR-17, FR-18, FR-19).
4. The evaluation runs the six prepared answers per frozen essay question three times and reports the ranking result (FR-29, SM-5).
5. Demo Mode shows prepared example answers with stored feedback (FR-23).

## Boundaries

Essay generation, feedback, submissions, drafts, the essay screen, the ranking check and demo content. Not new scoring rules for other quiz types.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-16, FR-17, FR-29, SM-5
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-5, AD-11, AD-13, AD-18
- design — _bmad-output/initiative-recall/ux-recall/wireframes/08-quiz-essay.md

## Notes

- Open question: how to compare the AI's covered key points with the builder's pre-marked points exactly (PRD open question 7).
- Open question: no test answer isolates spelling and grammar errors (PRD open question 8).
- Note: freezing the essay questions and writing the 6 prepared answers per question is human work; those stories are hitl.
- Decision: tracer bullet is story 2 (one essay answer rated through replay); story 1 is your human freezing step and can be done early at any free time after epic-evaluation story 1.
- Decision: no "Refactor sweep" closing story in this epic (user, 2026-10-18).
- Note: FR-18, FR-19, FR-23 and FR-26 are shared with earlier epics: this epic delivers only the essay parts (the essay results and Review List rules, the essay demo content, and the frozen essay questions).
- Tier: if-time, priority 2.
