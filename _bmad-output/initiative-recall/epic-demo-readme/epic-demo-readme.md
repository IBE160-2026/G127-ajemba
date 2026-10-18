---
type: epic
title: "Demo Mode and README"
parent: initiative-recall
covers: [FR-23, FR-24, SM-9]
after: []
assignee: ""
risk: medium
---

# Demo Mode and README

## Description

The examiner can run the app from a fresh clone with no key and no account. Demo Mode serves a pre-processed Example Lecture from stored data, through the same screens and tables as the real app, with a banner that states its limits. The README is started in epic 1 and each story adds its own section; the last story of this epic checks and polishes it from a fresh clone.

## Outcome

A fresh clone followed step by step starts in Demo Mode, and a visitor can read the Example Lecture's Summary and take the quizzes that exist (SM-9).

## Done when

1. With no API key the app starts; "Try the demo" is always visible on the login page and opens the Example Lecture with no login (FR-23).
2. The banner shows on every Example Lecture page and states the limits; uploading in Demo Mode shows the "needs an API key" message (FR-23).
3. The Example Lecture is read-only and quiz progress on it is kept only in the browser session (AD-10).
4. `.env.example`, the test PDF in `samples/`, and the README exist, and `fresh_clone_check.ps1` passes and is recorded in `docs/` (FR-24).
5. The README includes the "if you deploy this" section, the Google terms notice and "what we checked and what we did not" (AD-15, AD-16, PRD §5.7).

## Boundaries

Example data, demo replay, the demo banner, run scripts and documentation. Not new quiz types: Fill-in and Essay add their demo content in their own epics.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-23, FR-24, SM-9
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-10, AD-12, AD-15
- design — _bmad-output/initiative-recall/ux-recall/EXPERIENCE.md (Demo Mode banner)

## Notes

- Decision: Demo Mode and the README come before all extras so they are never the part that gets dropped (user, 2026-10-18).
- Assumption: the Example Lecture is built from the builder's own slides (test lecture 1) or freely licensed slides, with a real AI run reviewed by the builder (AD-10.8).
- Note: the README's "what we checked" section is written again when the evaluation epic finishes.
- Decision: tracer bullet is story 1 (open the demo with no key). Story 2 documents and proves it.
- Note: FR-23 is shared: this epic delivers the Summary and Multiple Choice demo content; epic-fill-in-gaps and epic-essay-feedback add their own content.
- Tier: must-have.
