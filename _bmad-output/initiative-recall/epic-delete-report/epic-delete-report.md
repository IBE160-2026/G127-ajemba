---
type: epic
title: "Delete a lecture and report a question"
parent: initiative-recall
covers: [FR-21, FR-22, FR-31]
after: []
assignee: ""
risk: low
---

# Delete a lecture and report a question

## Description

A student can delete one of their lectures, which removes all its content, and can report a question that looks wrong. The builder can export the reports to a file and review them. These are privacy and quality safeguards, not part of the main journey.

## Outcome

Deleted lectures are gone for good, and reports reach the builder with enough detail to act on.

## Done when

1. After deletion the lecture is gone from the list, its address returns 404, and all its summary, questions, attempts and page text are removed; a report keeps its snapshot (FR-21, AD-18.2).
2. A report stores the question, lecture, user, reason, timestamp and a snapshot, and the user sees a confirmation (FR-22).
3. `manage.py export_reports` writes all reports to a file (FR-31, AD-13.8).

## Boundaries

Delete and report only. No admin screen (PRD §8.2).

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-21, FR-22, FR-31
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-3.8, AD-8, AD-18

## Notes

- Decision: tracer bullet is story 1 (delete one lecture); the two stories are independent.
- Tier: if-time, priority 3.
