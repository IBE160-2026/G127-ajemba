---
title: 'Upload a PDF with all checks'
type: 'feature'
ticket: 'story-upload-a-pdf-with-all-checks'
created: '2026-11-19'
status: 'built'
baseline_revision: '35b6fe52bb17ab8eaba968504905d1b80f9ca5ae'
route: 'full'
route_source: 'auto'
risk: 'high'
review: 'quick'
review_source: 'pinned'
lenses_ran: [quick]
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** There is no way to get a lecture into the app. Story 2.1 gave `extract_pages`, but nothing checks a file before money or storage is spent (GitHub issue #11, FR-3, FR-4, SM-8).

**Approach:** One login-protected upload page. A service runs the AD-20 steps 1-4 and 6 in order (size, `%PDF-`, extraction in a subprocess with a 20 s limit, pages, text per page), then writes a `Lecture` (`processing`) plus `PageText` rows in one short transaction. No job is queued and no AI module is imported.

## Boundaries & Constraints

**Always:**
- Data minimisation: the PDF is never stored. Only a temporary file during checks; deleted in `finally`. No model gets a file field. Only extracted text is kept.
- Every temporary copy is deleted in all cases (failed check, timeout, crash): Django's temporary upload file and any file handed to the extraction subprocess. A test proves no temp file is left after a rejected upload. (Added by the human at approval.)
- Owner scoping: `PageText` is reachable only through the owner-scoped door (`for_user`, via its lecture's user), same as `Lecture` in 1.3. Wrong owner and missing id give the same bare `Http404` (AD-8.2).
- Extraction only through `core/pdf_text.py` (pypdf 7.1.1). No pdfplumber. No new package.
- No PDF read inside `atomic()` (AD-24).
- Messages are the exact EXPERIENCE.md texts.

**Never:** daily limit, upload notice or tick box, job queue, AI import (stories 3 and epic-summary); changing `extract_pages` or epic-1 access rules; keeping rejected files or rows.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Valid | text PDF, ≤50 pages, ≤10 MB | Lecture `processing`, PageText 1..n, redirect to lecture page | none |
| Too big | > 10 MB | read stops at 10 MB + 1 byte | "This file is larger than 10 MB. Choose a smaller file." |
| Not PDF | first bytes ≠ `%PDF-` | nothing created | "This file is not a PDF. Choose a PDF file." |
| 51 pages | valid header | nothing created | "This PDF has more than 50 pages. Choose a shorter file." |
| No text | scanned, encrypted, corrupt, <100 chars/page avg | nothing created | "This file has no text we can read. Choose a PDF with text, not a scan." |
| Timeout | extraction > 20 s | process killed | same no-text message |
| No file | empty submit | nothing created | "Choose a PDF file." |
| Logged out | GET/POST upload | redirect to login | none |

</frozen-after-approval>

## Code Map

- `core/pdf_text.py` -- `extract_pages`, `average_chars_per_page`; reuse, do not change.
- `lectures/models.py` -- `Lecture` (+`for_user`); add `PageText` (lecture FK CASCADE, number, text, unique(lecture, number)) with owner-scoped manager.
- `lectures/services.py` -- `get_lecture` door; add upload service and `_extract_in_subprocess`.
- `lectures/views.py`, `lectures/urls.py` -- add `upload` view at `upload/` (declare before `<int:...>`).
- `config/urls.py` -- `lectures/` include already mounted.
- `config/settings.py` -- add `DATA_UPLOAD_MAX_MEMORY_SIZE`, `FILE_UPLOAD_HANDLERS` (temp-file handler), limits constants.
- `templates/lectures/upload.html`, `templates/base.html` -- form (CSRF, `enctype`), nav link "Upload", rules list from wireframe 03.
- `docs/required_readme_headings.txt`, `README.md` -- add "Upload limits"; fix line 100 ("no upload page yet").
- `lectures/tests.py`, `lectures/migrations/0002_pagetext.py` -- tests and migration.

## Tasks & Acceptance

**Execution:**
- [ ] `lectures/models.py` + migration -- `PageText` with `PageTextQuerySet.for_user` -- owner-scoped like Lecture
- [ ] `lectures/services.py` -- `create_lecture_from_upload(user, uploaded_file)` raising `UploadRejected(message)`; temp file in `finally`; subprocess (`sys.executable -I -c`, `timeout=20`) printing JSON pages; `atomic()` only for the write; title = filename stem, max 200
- [ ] `lectures/views.py`, `urls.py`, `upload.html`, `base.html` -- login-required form, error message shown, success redirect to `lecture_detail`
- [ ] `config/settings.py` -- 10 MB stream cap and constants
- [ ] `lectures/tests.py` -- tests named in the story, plus other-user 404 for page text and a check that no file is left in the temp dir
- [ ] `README.md`, headings file -- "Upload limits"

**Acceptance Criteria:**
- Given the story ACs 1-9, when `python manage.py test` runs, then all pass.
- Given a rejected upload, when it ends, then no Lecture/PageText row, no leftover temp file, and `lectures.services` imports no AI module.

## Implementation Notes

Implemented directly (no coding subagent). Added `core/extract_cli.py` (subprocess entry), `lectures/upload_handlers.py` (stops writing at 10 MB + 1 byte; sets `request.upload_too_big`), `evaluation/make_test_fixtures.py` + `lectures/test_fixtures/encrypted.pdf` (pypdf stays out of app tests). Human addition at approval: every temporary copy deleted on all paths, with tests. No package installed. Test server was never started; checks ran through Django's test client.

## Plan Change Log

## Review Triage Log

Quick lens, 8 findings (no loopback).
- medium / patch -- Django saved the whole body before the 10 MB check. Fixed with `LimitedTemporaryFileUploadHandler` + tests.
- low / patch -- timeout test too weak. Now uses a 60 s sleeper child and checks the call returns in under 20 s.
- low / patch -- 50-page test asserted too little. Now checks redirect and Lecture.
- low / patch -- the HTTP over-10 MB test did not show early stop. Covered by the handler unit test.
- medium / defer -- no memory cap in the subprocess (AD-20); written to deferred-work.md.
- low / rejected -- page count checked after full extraction; AD-20 order, bounded by the 20 s limit.
- false -- rules list differs from wireframe: it matches; the daily-limit line is story 3.
- pending at review time -- session log; written after review.

## Design Notes

- The memory cap in AD-20 has no portable Windows implementation; only the 20 s limit is enforced. Recorded as an open point in the log.
- Subprocess reading from a path (not stdin) keeps the file in one place for deletion.

## Verification

**Commands:**
- `python manage.py test` -- expected: all tests pass
- `python manage.py makemigrations --check` -- expected: no changes

**Manual checks (if no CLI):**
- Start `python run.py --port 8001`, upload a valid and a scanned PDF, confirm messages; then stop the server.
