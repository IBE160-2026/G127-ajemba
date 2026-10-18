---
id: 2
type: story
title: "Upload a PDF with all checks"
parent: epic-upload-pdf-checks
covers: [FR-3, FR-4, SM-8]
after: [1, 1.3]
refined: true
hitl: false
risk: high
---

# Upload a PDF with all checks

## Description

A logged-in user can upload one PDF. The app checks it in a fixed order before spending anything: size while streaming, the `%PDF-` header, text extraction in a separate process with a time limit, page count, and readable text. A valid file becomes a Lecture in status `processing` with one PageText row per page. A rejected file creates nothing and makes no AI call. No job is queued yet; that is added in epic-summary.

## Acceptance Criteria

1. **A valid file is stored as text only**
   **Given** a logged-in user and a valid text-based PDF of 50 pages or fewer and 10 MB or less
   **When** they upload it
   **Then** a Lecture owned by that user exists in status `processing` with one PageText row per page numbered from 1, and the PDF itself is not kept
2. **Too big is rejected**
   **Given** a file over 10 MB
   **When** it is uploaded
   **Then** reading stops at 10 MB plus one byte and the message states the 10 MB limit, with no Lecture created
3. **Not a PDF is rejected**
   **Given** a file whose first bytes are not `%PDF-`, whatever its name says
   **When** it is uploaded
   **Then** a clear message says the file is not a PDF and no Lecture is created
4. **Too many pages is rejected**
   **Given** a PDF of 51 pages
   **When** it is uploaded
   **Then** the message states the 50-page limit and no Lecture is created
5. **No readable text is rejected**
   **Given** a scanned PDF, an encrypted PDF, a corrupt PDF, or a PDF with fewer than 100 characters of text per page on average
   **When** it is uploaded
   **Then** the message says the file has no readable text and no Lecture is created
6. **A hostile PDF cannot hang the app**
   **Given** extraction that takes longer than 20 seconds
   **When** a PDF is uploaded
   **Then** the extraction process is stopped and the user sees the no-readable-text message
7. **Rejection means no cost and no leftovers**
   **Given** any rejected upload
   **When** it finishes
   **Then** no Lecture or PageText row exists, the temporary file is deleted, and no AI call was made (the upload code imports no AI module)
8. **Only signed-in users upload**
   **Given** a logged-out visitor
   **When** they open the upload address
   **Then** they are redirected to login
9. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** an "Upload limits" section states the 10 MB and 50-page limits and that scanned or image-only PDFs are rejected

## Tests

- `test_readme_has_required_sections` (adds "Upload limits" to the list)
- `test_fr3_rejects_file_over_10mb`, `test_fr3_rejects_non_pdf`, `test_fr3_rejects_over_50_pages`
- `test_fr4_rejects_image_only_pdf`, `test_fr4_rejects_encrypted_and_corrupt_pdf`
- `test_sm8_rejected_upload_creates_nothing_and_calls_no_ai`
- `test_fr3_valid_upload_creates_lecture_with_page_rows`
- `test_extraction_timeout_gives_no_text_message` (timeout set low in the test)
- Messages are the plain texts in EXPERIENCE.md

## Boundaries

- Must not change: access rules from epic 1, `extract_pages` behaviour from story 1. The notice and the daily limit come in story 3; until then there is no limit.

## References

- parent — _bmad-output/initiative-recall/epic-upload-pdf-checks/epic-upload-pdf-checks.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-9, AD-18.7, AD-20, AD-24
- design — _bmad-output/initiative-recall/ux-recall/wireframes/03-upload.md, EXPERIENCE.md (state patterns and messages)
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-3, FR-4, SM-8

## Notes

- Assumption: PDFs for tests are small generated fixtures (an over-limit file is made in the test, not committed).
- Risk check: a transaction holds only the final write; no PDF read happens inside `atomic()` (AD-24).
