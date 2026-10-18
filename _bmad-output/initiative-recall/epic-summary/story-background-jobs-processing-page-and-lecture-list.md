---
id: 2
type: story
title: "Background jobs, Processing page and lecture list"
parent: epic-summary
covers: [FR-5]
after: [2.2]
refined: true
hitl: false
risk: high
---

# Background jobs, Processing page and lecture list

## Description

Work no longer waits for the open page. One worker runs jobs behind a single `jobs.enqueue` call, and every status change goes through one safe function, so a job can never run twice. The user sees a Processing page with real steps and a My lectures list with Processing, Ready and Failed. A failed lecture has a retry button, at most 3 times. Until the Summary is built in story 3, the job body is a stub that ends the lecture as Failed; it is replaced there.

## Acceptance Criteria

1. **A job runs even if the page closes**
   **Given** an uploaded lecture in `processing`
   **When** the user closes the page
   **Then** the worker still finishes the job and the lecture shows Ready or Failed in the list later
2. **A job runs once**
   **Given** the same lecture id enqueued twice
   **When** the worker runs
   **Then** only the first run changes the status (`set_status` returns `False` for the second), and the second stops without work
3. **Only ids go through the queue**
   **Given** `jobs.enqueue(name, object_id)`
   **When** a job is queued
   **Then** the job receives an integer id and returns nothing, no text is stored in queue tables, and enqueue happens in `transaction.on_commit`
4. **Stuck lectures are caught**
   **Given** a lecture in `processing` for longer than `STALE_MINUTES` (10)
   **When** `run.py` starts or the status view is read
   **Then** it is treated as `failed` and shows the retry button
5. **Retry is limited**
   **Given** a failed lecture
   **When** the user presses retry
   **Then** the lecture returns to `processing` (a POST request) up to 3 times, and a fourth try is refused with a plain message
6. **The Processing page is honest**
   **Given** a processing lecture
   **When** the page loads
   **Then** it shows "Reading your PDF" as done and "Writing the summary" in progress, no percentage and no timer, polls `/status/lecture/<id>/` every 3 seconds, and stops polling at Ready or Failed
7. **The list shows real status**
   **Given** the My lectures page
   **When** it loads
   **Then** it lists only the user's lectures with Processing…, Ready or Failed, and a Failed one shows a clear message and the retry button
8. **The worker starts with the app**
   **Given** `python run.py`
   **When** it starts
   **Then** the web app and the worker run together and Ctrl+C stops both, and a Windows test of django-q2 is recorded in `docs/`; if the cluster does not run on Windows, the thread-based fallback behind the same interface is used and tested the same way

9. **AI cost caps hold**
   **Given** the settings `AI_CALLS_PER_USER_PER_DAY` and `AI_CALLS_GLOBAL_PER_DAY`
   **When** a job is about to be queued and either budget, read from `AiCallLog`, is used up
   **Then** nothing is queued, the user sees a clear message, and retries stay capped at 3 per lecture
10. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "How processing works" section says that `run.py` starts the web app and the worker together, and an "If you deploy this" section lists debug off, a real `SECRET_KEY`, allowed hosts, HTTPS, Waitress, one worker, a paid AI key, a privacy review, and that the SQLite file is the only copy

## Tests

- `test_readme_has_required_sections` (adds "How processing works" and "If you deploy this" to the list)
- `test_ad23_job_not_queued_when_ai_budget_used_up`
- `test_fr5_job_finishes_after_page_closed`
- `test_fr5_job_runs_once_when_enqueued_twice`
- `test_fr5_stale_processing_becomes_failed`
- `test_fr5_retry_limited_to_three`
- `test_job_arguments_are_ids_only`
- `test_status_view_other_user_gets_404`
- Manual: start `run.py`, upload, close the browser tab, reopen the list

## Boundaries

- Must not change: upload validation and daily limit; the owner-scoped access rules. The Summary itself is story 3.

## References

- parent — _bmad-output/initiative-recall/epic-summary/epic-summary.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-3, AD-11.1, AD-15.1, AD-22, AD-24
- design — _bmad-output/initiative-recall/ux-recall/wireframes/02-my-lectures.md and 04-processing.md; EXPERIENCE.md (Flow 3)
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-5

## Notes

- Unknown: whether django-q2 works on Windows. Settled in this story; the fallback is already accepted (AD-3.3).
- Note: if the whole story does not fit in 2 hours, split the Processing page and list from the job system.
