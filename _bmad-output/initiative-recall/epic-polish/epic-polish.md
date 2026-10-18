---
type: epic
title: "Polish: text size and accessibility check"
parent: initiative-recall
covers: []
after: []
assignee: ""
risk: low
---

# Polish: text size and accessibility check

## Description

The student can change the text size and the choice is kept on that device. An automated Lighthouse accessibility check is run on the main pages and the result is recorded. This epic owns no FR ids; it delivers the cross-cutting requirements in PRD §6.3.

## Outcome

The main pages score 90 or higher in Lighthouse accessibility and the text-size control works on every page.

## Done when

1. The text-size control offers normal, large and extra large, and the choice is kept on the device (PRD §6.3).
2. Lighthouse accessibility is 90 or higher on the main pages, and results are recorded in `docs/`.
3. Fixes found by the check are made, or listed as known gaps in the README.

## Boundaries

Cross-cutting visual and accessibility polish only. No new features.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, §6.3 Accessibility and Readability
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-1 (app.js), AD-22
- design — _bmad-output/initiative-recall/ux-recall/DESIGN.md and review-accessibility.md

## Notes

- Decision: one story, so it is its own tracer bullet.
- Tier: if-time, priority 4 (last; first to drop).
