---
type: epic
title: "Fill-in-the-gaps"
parent: initiative-recall
covers: [FR-14, FR-15, FR-23, SM-4]
after: []
assignee: ""
risk: low
---

# Fill-in-the-gaps

## Description

A student practises key terms by typing the missing word in a sentence from the lecture. Eight questions are generated once and stored; typed answers are checked by fixed rules with no AI. The quiz reuses the scoring, results and Review List already built for Multiple Choice, and is added to the evaluation and to Demo Mode.

## Outcome

Typed answers are accepted or rejected exactly as the examples in FR-15 say (SM-4).

## Done when

1. Eight questions are generated and stored, each with one expected term, a Summary Part link and a Source Reference (FR-14).
2. All example tests in FR-15 pass, including case, spaces, one wrong letter for terms of five letters or more, and exact match for shorter terms (FR-15, SM-4).
3. Skipping a question counts as wrong and creates a Review List entry (FR-15, FR-19).
4. The evaluation checks fill-in answer keys, and the Example Lecture has fill-in content for Demo Mode.

## Boundaries

Fill-in generation, the matching module, the quiz screen and the additions to evaluation and demo data. Not essays.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-14, FR-15, SM-4
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-2, AD-21
- design — _bmad-output/initiative-recall/ux-recall/wireframes/07-quiz-fill-in-the-gaps.md

## Notes

- Decision: tracer bullet is story 1 (the matching rules, no AI); story 2 builds on it.
- Note: FR-23 is shared: this epic delivers only the fill-in demo content.
- Tier: if-time, priority 1 after the evaluation.
