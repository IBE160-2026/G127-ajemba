---
type: epic
title: "Summary with source references"
parent: initiative-recall
covers: [FR-5, FR-8, FR-9, FR-10, FR-11, FR-25, FR-27, SM-1, SM-2]
after: []
assignee: ""
risk: high
---

# Summary with source references

## Description

The background worker, the AI client and the Summary prompt are built, and an uploaded Lecture is turned into a plain-language Summary with Summary Parts, Source References and Key Terms. Every AI answer is checked before it is stored, and bad answers are retried at most twice. The user sees real processing steps, can leave the page, and can retry on failure.

## Outcome

A user who uploads a text-based PDF gets a validated Summary within 60 seconds (up to 30 pages), each part showing valid slide numbers (SM-1, SM-2).

## Done when

1. A valid upload is processed in the background and ends as Ready or Failed; leaving the page does not stop it, and a failure shows a message and a retry button (FR-5).
2. The Summary page shows Summary Parts with Source References, Key Terms with explanations, and the AI-generated notice (FR-8, FR-9, FR-11).
3. Deliberately broken AI responses are rejected and retried at most twice, then the lecture fails cleanly; no partial Summary is ever stored (FR-27).
4. The Summary prompt is a versioned file with the plain-language instruction (FR-10, FR-25).
5. A real Summary of test lecture 1 is generated within the time limit and recorded (SM-1).

## Boundaries

The job system, `ai_client.py`, the Summary prompt, the validators and the Summary and Processing pages. Not quiz generation (epic-multiple-choice-results). Only `ai_client.py` imports the Gemini library; only `jobs.py` imports django-q2.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-5, FR-8 to FR-11, FR-25, FR-27, SM-1, SM-2
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-3, AD-4, AD-5, AD-6, AD-11, AD-18, AD-21, AD-23
- design — _bmad-output/initiative-recall/ux-recall/wireframes/04-processing.md and 05-summary.md

## Notes

- Decision: build order step 3 is the AI client and Summary, after the user model and the FR-4 test (user, 2026-10-18).
- Unknown: the exact Gemini model and how structured output is called in google-genai; spike both styles before the AI client is built and record the date (architecture, Deferred).
- Unknown: whether django-q2 runs on Windows; if not, use the thread-based fallback behind the same interface (AD-3.3).
- Note: a minimal "My lectures" list showing Processing, Ready and Failed is part of this epic; the full list with past attempts is in epic-multiple-choice-results.
- Decision: tracer bullet is story 3: a replayed upload goes from processing to a stored Summary. Story 1 (AI client) and story 2 (jobs) come first because both are needed; story 5 is a checkpoint before the quizzes.
- Decision: no "Refactor sweep" closing story in this epic (user, 2026-10-18).
- Parked: SM-1 for PDFs of 31 to 50 pages (under 120 seconds) is not measured, because the test lectures are 10-12 slides; the README says so in "what we checked and what we did not". The 30-page limit is shown only on a 10-12 page file.
- Tier: must-have.
