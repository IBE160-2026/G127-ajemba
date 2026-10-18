---
type: epic
title: "Upload and PDF checks"
parent: initiative-recall
covers: [FR-3, FR-4, FR-6, FR-7, SM-8]
after: []
assignee: ""
risk: high
---

# Upload and PDF checks

## Description

First the builder finds or makes the test slides and runs the FR-4 text-extraction test on a real PowerPoint-exported PDF, recording the result. Then a logged-in user can upload one PDF, and the app checks it before any AI cost: size, page count, readable text, the one-time notice about external AI processing, and the daily limit. A rejected file creates no Lecture and makes no AI call.

## Outcome

A user can upload a valid text-based PDF and get a stored Lecture with per-page text; every invalid file is rejected with a clear message (SM-8).

## Done when

1. A human step is done: test lecture 1 (own slides, PowerPoint to PDF) exists and the extraction result and chosen library are recorded in `docs/` (FR-4, AD-9).
2. PDFs over 50 pages or 10 MB, non-PDF files and scanned PDFs are rejected with the messages in EXPERIENCE.md, create no Lecture and make no AI call (FR-3, FR-4).
3. A user who has not acknowledged the notice cannot upload; the notice matches the stored Google quotes (FR-6).
4. A sixth upload on one day is rejected; rejected uploads do not count (FR-7).
5. A valid upload creates a Lecture in status `processing` with one PageText row per page (AD-20).

## Boundaries

Everything from the file chooser to the stored per-page text. Not the AI call or the Summary (epic-summary). Only `pdf_text.py` imports pdfplumber.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-3, FR-4, FR-6, FR-7, SM-8
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-9, AD-15, AD-16, AD-20, AD-21
- design — _bmad-output/initiative-recall/ux-recall/wireframes/03-upload.md
- constraint — _bmad-output/initiative-recall/architecture-recall/gemini-terms-checked-2026-10-17.md

## Notes

- Decision: first story is a human step; test lecture 1 is the builder's own PowerPoint slides on a topic they know (likely nursing). Test lecture 2 is a freely licensed deck (for example OpenStax) with the licence checked and credited in the repo; no lecturer course material. Two test lectures in total, each about 10-12 slides (user, 2026-10-18).
- Decision: build order step 2 is the FR-4 test on a real PowerPoint PDF, before any Summary work (PRD §6.5, architecture AD-9).
- Unknown: whether pdfplumber output is clean enough or pypdf is better; settled by the FR-4 test story.
- Unknown: the 100 characters per page threshold may need tuning (PRD open question 4); settled after the first extraction check.
- Decision: tracer bullet is story 1 (a real PDF goes through `extract_pages`); the upload page builds on it. The notice and daily limit come last because they only gate an upload that already works.
- Tier: must-have.
