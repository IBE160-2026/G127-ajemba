---
id: 3
type: story
title: "Upload notice acknowledgement and daily limit"
parent: epic-upload-pdf-checks
covers: [FR-6, FR-7, SM-8]
after: [2, 1.2]
refined: true
hitl: false
risk: medium
---

# Upload notice acknowledgement and daily limit

## Description

Before a user's first upload, the upload page shows the notice that lecture text and essay answers go to Google Gemini, quoting Google's terms exactly, and the user must acknowledge it. The server refuses any upload without a current acknowledgement. Each user may upload 5 PDFs per day; the limit is a setting.

## Acceptance Criteria

1. **No upload without acknowledgement**
   **Given** a user whose `notice_ack_at` is empty
   **When** they post a valid PDF
   **Then** the upload is refused by the server, no Lecture is created, and the notice is shown
2. **Acknowledging unlocks upload**
   **Given** the notice on the upload page
   **When** the user ticks the box and submits
   **Then** `notice_ack_at` and the current `notice_version` are stored, and the next valid upload works without showing the notice again
3. **The notice is Google's words, exactly**
   **Given** the quotes stored in `gemini-terms-checked-2026-10-17.md`
   **When** the notice test compares them with the notice text
   **Then** every stored quote appears word for word, including the passage for the EEA, Switzerland and the UK
4. **A changed notice asks again**
   **Given** a user who acknowledged an older `notice_version`
   **When** the current version is higher
   **Then** the user must acknowledge again before uploading
5. **Daily limit**
   **Given** a user who has uploaded 5 valid PDFs today (local date in `LIMIT_TIME_ZONE`, default `Europe/Oslo`)
   **When** they upload a sixth
   **Then** it is rejected with a clear message, no Lecture is created, and no AI call is made
6. **Only accepted uploads count**
   **Given** uploads rejected for size, type, pages or no text
   **When** the daily count is read
   **Then** they are not counted, and the count and the new Lecture are written in one transaction after validation
7. **The limit is a setting**
   **Given** `UPLOADS_PER_DAY` set to 2
   **When** a third upload is tried
   **Then** it is rejected, and at local midnight the count starts again
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** an "AI notice and daily limit" section quotes Google's notice exactly with its source link and the date it was checked, and names the `UPLOADS_PER_DAY` setting

## Tests

- `test_readme_has_required_sections` (adds "AI notice and daily limit" to the list)
- `test_fr6_upload_refused_without_acknowledgement`
- `test_fr6_notice_contains_stored_google_quotes`
- `test_fr6_new_notice_version_requires_new_acknowledgement`
- `test_fr7_sixth_upload_rejected`, `test_fr7_rejected_files_do_not_count`
- `test_fr7_day_boundary_uses_oslo_time` (fixed clock)

## Boundaries

- Must not change: the validation order and messages from story 2. The README copy of the notice is made in epic-demo-readme.

## References

- parent — _bmad-output/initiative-recall/epic-upload-pdf-checks/epic-upload-pdf-checks.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-15.5, AD-16, AD-20
- design — _bmad-output/initiative-recall/ux-recall/EXPERIENCE.md, "Upload notice (exact text)"
- quotes — _bmad-output/initiative-recall/architecture-recall/gemini-terms-checked-2026-10-17.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-6, FR-7, SM-8

## Notes

- Decision: free Gemini key is used only by the builder locally in v1 (AD-16.7); this story does not change that.
- Note: deleting a lecture must not reduce the daily count; that test is added in epic-delete-report.
