---
type: epic
title: "Slim evaluation on the Test Set"
parent: initiative-recall
covers: [FR-26, FR-28, FR-30, SM-10, SM-11, SM-C1, SM-C2, SM-C3]
after: []
assignee: ""
risk: medium
---

# Slim evaluation on the Test Set

## Description

The builder freezes 2 test lectures with their Reference Key Points, then one command runs them through the real AI and writes a report with a review sheet. A second command refuses to finish until every box is ticked and then prints pass or fail. This slim version covers only what the core produces: Summary completeness and faithfulness, and Multiple Choice grounding and answer keys, plus the automatic checks.

## Outcome

The repository holds a dated evaluation report, tied to prompt versions, that shows how well the AI's Summary and Multiple Choice output meets the PRD targets (SM-10, SM-11).

## Done when

1. Each Test Set lecture has at least five Reference Key Points, written and committed before any AI output is judged; a test fails if frozen files change (FR-26, AD-13.5).
2. `evaluate` runs the lectures, writes a report with the date, model and prompt versions, and a review sheet (FR-28).
3. `evaluate --finish` refuses while any box is unticked and then prints the result against the SM-10 targets (AD-13.2).
4. `evaluate --compare` shows the difference between two reports, and the prompt fingerprint rule is enforced (FR-30, AD-6).
5. A real report for the Test Set is stored in `evaluation/reports/`, with counts for SM-C1 to SM-C3.

## Boundaries

The `evaluate` command, the Test Set files, the review sheet and the report. Never runs inside `manage.py test`. Essay ranking (FR-29) and fill-in checks come later in their own epics.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-26, FR-28, FR-30, SM-10, SM-11, §5
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-6, AD-13, AD-14

## Notes

- Decision: slim version only: Summary completeness and faithfulness, Multiple Choice grounding and answer keys, on 2 test lectures (user, 2026-10-18).
- Decision: two test lectures of about 10-12 slides each: the builder's own slides plus one freely licensed deck with the licence credited in the repo (user, 2026-10-18).
- Open question: definition of "unsupported statement" for faithfulness and what happens if the target cannot be met (PRD open question 6); settle before the first run.
- Note: writing the Reference Key Points is human work; those stories are hitl.
- Note: daily rate limits may spread a run over several days (AD-13.4).
- Decision: tracer bullet is story 2 (evaluate on replay data). Story 1 (your frozen Test Set) can be done at any free time after epic 2 story 1, even before the AI work is finished.
- Decision: no "Refactor sweep" closing story in this epic (user, 2026-10-18).
- Tier: must-have.
