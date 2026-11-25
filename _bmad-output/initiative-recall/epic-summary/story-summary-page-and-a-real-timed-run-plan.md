---
title: 'Summary page and a real timed run'
type: 'feature'
ticket: '4'
created: '2026-11-25'
status: 'built'
baseline_revision: '80fb77d5f13b9a282799c7774333d7f7eccd0a64'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: ['{project-root}/_bmad-output/initiative-recall/epic-summary/story-summary-page-and-a-real-timed-run.md', '{project-root}/_bmad-output/initiative-recall/ux-recall/wireframes/05-summary.md', '{project-root}/_bmad-output/initiative-recall/ux-recall/DESIGN.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A Ready lecture shows "Summary coming soon". The stored Summary cannot be read, and the real timing (SM-1) and slide-number check (SM-2) are not recorded.

**Approach:** Add the Summary page at `/lectures/<id>/summary/` following `wireframes/05-summary.md`, with the DESIGN.md tokens and the WCAG review fixes A1, A2, A4, A5, A8, A12 and A14. Add `format_slides()`, a no-Gemini `check_summary` command, `docs/summary-timing.md` and the README addition. The timed run is the user's manual step.

## Boundaries & Constraints

**Always:**
- Owner-scoped: the page reads through `get_lecture` and `for_user`; wrong owner and missing id give the identical 404; logged-out visitors are redirected to login. A lecture that is not Ready redirects to its Processing page.
- AI text (heading, text, term, explanation) is plain escaped text. No `|safe`, `mark_safe`, `autoescape off` or markdown in any template.
- Every test blocks real Gemini (`no_real_calls` from story 3.3). Python is `.venv/Scripts/python`.
- Wireframe 05 is followed for: AI notice, "Jump to" list, numbered parts with anchors, source chip, key terms panel beside each part (wide) or below (phone), one page address and one page title ("Summary – Title – Recall"), `lang` on lecture content, chips 44px high with the accessible name "Slides 12 to 15, Heading".

**Never:**
- Leave out (later stories): the quiz and Results tabs and the tab row, the Text size control, the Demo banner, the phone "Menu" button, inline tap-or-hover term help, the link back to a question, and a site-wide restyle (epic-polish). Do not change stored rows, validators or the job.
- No real Gemini call by me. No new package. Never read `.env`. No commit of code.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Owner, Ready | parts with refs [12,13,14,15] | heading, text, chip "Slides 12 to 15", its key terms, AI notice | none |
| Few slides | [3,7,12] / [4,5] / [9] | "Slides 3, 7 and 12" / "Slides 4 and 5" / "Slide 9" | none |
| Text has `<script>` | stored text | shown as escaped text | none |
| Other user, missing id, logged out | request | same 404 body / login redirect | no data |
| Not Ready | processing or failed | redirect to Processing page | none |

</frozen-after-approval>

## Code Map

- `lectures/views.py`, `lectures/urls.py` -- add `lecture_summary`; `lecture_detail` sends Ready lectures to it.
- `lectures/services.py` -- `get_summary(user, lecture_id)` via `get_lecture` and `SummaryPart.objects.for_user`.
- `core/text_utils.py` -- add pure `format_slides(slides)`.
- `templates/lectures/summary.html`, `templates/_ai_notice.html` (shared, reused by quiz pages), `templates/base.html` (`main_class` block).
- `static/css/recall.css`, `static/js/summary_focus.js` -- scoped summary styles; focus moves to the heading of a `#part-N` link (no inline script, CSP).
- `lectures/management/commands/check_summary.py` -- checks every Source Reference slide exists in the stored page count (SM-2); no AI.
- `lectures/test_summary_page.py`, `core/test_format_slides.py` -- tests; `README.md`, `docs/summary-timing.md`.
- Reuse: `test_summary_job.no_real_calls`, `make_lecture`; `config/tests.py` README test. Do not touch `core/validation.py`, `jobs.py`.

## Tasks & Acceptance

**Execution:**
- [ ] `core/text_utils.py`, `core/test_format_slides.py` -- `format_slides` and `test_format_slides_runs_and_lists`
- [ ] `lectures/services.py`, `views.py`, `urls.py` -- owner-scoped summary view and redirects
- [ ] templates, CSS, JS -- page per wireframe 05 and the WCAG fixes
- [ ] `lectures/test_summary_page.py` -- the named tests (FR-8, FR-9, FR-11, AD-5 escaping and no-safe scan, owner-only incl. identical 404), all with Gemini blocked
- [ ] `check_summary.py` -- SM-2 command and test
- [ ] `docs/summary-timing.md`, `README.md` -- timing record (empty until the manual run) and the "31 to 50 pages not timed" statement

**Acceptance Criteria:**
- Given a Ready lecture of user A, when A opens its Summary, then parts, chips, key terms and the AI notice show; user B and anonymous get the 404 or login redirect.
- Given the manual run, when the user fills `docs/summary-timing.md`, then the time, model and prompt version are recorded and a miss is stated as a finding.

## Implementation Notes

## Plan Change Log

## Review Triage Log

Pass 1 (quick, reviewer subagent): 8 findings.
- Processing page had no link to the Summary after the htmx swap -- medium -- patch: link added to `_status.html`, dead "coming soon" line removed, test added.
- `check_summary` said OK with no parts or a non-ready lecture -- medium -- patch: now reports problems; test added.
- Missing tests (terms per part, lang, empty terms, failed redirect) -- low -- patch: tests added.
- SM-2 compares with row count, not PDF pages -- false -- `create_lecture_from_upload` stores a row for every page, empty ones too.
- AI notice is a shared partial, not in base.html -- low -- not changed; plan chose the partial so quiz pages reuse it.
- Chip links to its own part -- low -- not changed; wireframe 05 specifies chips as links to the part.
- AC 6 and 8 open -- manual timed run by the user; README says "not run yet".
- Escaping scan is narrow -- low -- not changed.

Found by the user's manual timed run (2026-11-25, lecture 13): Google returned 503 twice in a row and the job failed after the one allowed retry; about 4 of 7 real calls that day gave 503. -- medium (real, hits the SM-1 run) -- route: proposal shown to the user, code not changed yet. Proposed: retry 503 and 429 up to 3 times with waits 2, 5 and 10 seconds, inside the shared job budget, never when the error says "limit: 0". Status: user said yes (3 retries, 2/5/10 s, per-user limit stays 30); implemented in `core/ai_client.py` and `config/settings.py` (`AI_RETRY_WAITS_S`).

Pass 2 (reviewer subagent on the retry diff):
- A wait equal to the remaining budget spent a rate slot with no request -- low -- patch: the check is now `wait >= remaining`.
- The `job_budget` exit logged nothing -- low -- patch: warning line with code and retry number, no content.
- Worst case 12 requests (busy counter restarts per validation attempt) not stated -- low -- patch: README sentence and a test (503 x3, bad answer, 503, good = 6 requests, Ready).
- Test name `test_429_twice...` wrong after the change -- low -- patch: renamed.
- 429 that is a per-minute quota is retried and `Retry-After` is ignored -- low -- not changed; as specified.
- Settings wiring test, zero waits, non-ASCII digits, total waits over the 220 s budget, old env name `AI_RETRY_WAIT_S` ignored silently -- low -- not changed; safe at run time because every wait is checked against the budget.

## Design Notes

Real-call count for one upload of a 12-slide PDF: normally **1**. At most 3 attempts (one plus two validation retries); each can add one short retry after a 503/429, so at most 6 requests. Replay and tests: 0.

## Verification

**Commands:**
- `.venv/Scripts/python manage.py test` -- expected: all pass, no network
- `.venv/Scripts/python manage.py check` -- expected: no issues
