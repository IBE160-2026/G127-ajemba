---
id: 5
type: story
title: "Checkpoint: compare real hours with estimates and adjust the cut"
parent: epic-summary
after: [4]
refined: true
hitl: true
risk: low
---

# Checkpoint: compare real hours with estimates and adjust the cut

## Description

A short pause after epic 3. **This is your step, no code:** write down the hours you actually spent on epics 1 to 3, compare them with the plan, and decide whether the cut of the remaining epics still fits before the deadline. This is the point where the plan is allowed to change.

## Acceptance Criteria

1. **Real hours are recorded**
   **Given** the three finished epics
   **When** you write the time log
   **Then** `docs/time-log.md` lists hours spent per story for epics 1 to 3, next to the plan (epic 1: 5.8 hours, epic 2: 6, epic 3: 8.1, which already include the README part of each story)
2. **The remaining work is recalculated**
   **Given** the real hours per story
   **When** the remaining must-have stories (epics 4 to 6) are re-estimated with the same ratio
   **Then** the log shows the hours left until the end of November and whether they fit
3. **The cut is decided**
   **Given** the result
   **When** it does not fit
   **Then** you name which story or epic is dropped first (candidates: merge 4.1 into 4.2, shrink 5.2 to its steps 5 and 6, or move 6.3's real run to the end; the README is never a candidate, because its parts are written inside each story), and a dated `Decision:` line with hours spent and the cut that remains is added to the initiative Notes
4. **The plan stays honest**
   **Given** the decision
   **When** it changes the cut
   **Then** the affected `tickets.toml` files and the README's "what we checked" plan are updated to match

## Tests

- No automated test. Proved by the time log, the Decision line in `initiative-recall.md`, and a re-run of the ticket status check with no problems.

## Boundaries

- Must not change: stories already done. Do not rewrite finished work as new work.

## References

- parent — _bmad-output/initiative-recall/epic-summary/epic-summary.md
- initiative — _bmad-output/initiative-recall/initiative-recall.md, Notes (cut and priority order)

## Notes

- Decision: this checkpoint was added on 2026-10-18 by the builder so that the cut is checked against real time before the quizzes are built.
