---
title: 'Upload notice acknowledgement and daily limit'
type: 'feature'
ticket: 'story-upload-notice-acknowledgement-and-daily-limit'
created: '2026-11-19'
status: 'built'
baseline_revision: 'ca20d16fc4893ef7d4cdc518ca2009375b1eed34'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: [quick]
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Story 2.2 accepts any PDF from any logged-in user. Nothing yet tells the user that text goes to Google Gemini, and nothing limits AI cost per user (GitHub issue #13, FR-6, FR-7, SM-8).

**Approach:** The upload service refuses an upload unless the user has acknowledged the current `notice_version`. After all file checks pass, one transaction counts today's `UploadLog` rows, rejects over the limit, and otherwise writes the `Lecture`, `PageText` rows and one `UploadLog` row. The day is the local date in `LIMIT_TIME_ZONE`.

## Boundaries & Constraints

**Always:**
- Keep story 2.2's rules: the PDF is never stored, every temporary copy is deleted on every path (including a refusal for missing acknowledgement or the limit), no PDF read inside `atomic()`, no AI import.
- Owner scoping: `UploadLog` is reachable only through `for_user`. Wrong owner and missing id give the same bare `Http404`. The notice acknowledgement is only ever written to `request.user`.
- Notice text is EXPERIENCE.md "Upload notice (exact text)", word for word. Its link is https://ai.google.dev/gemini-api/terms.
- Only accepted uploads count. Rejections for notice, size, type, pages, no text and the limit itself write no `UploadLog` row.
- `UPLOADS_PER_DAY` (default 5) and `LIMIT_TIME_ZONE` (default `Europe/Oslo`) are settings read in `config/settings.py`; a bad zone name or a value below 1 stops startup with `ImproperlyConfigured`. `TIME_ZONE` stays UTC. No new package (`tzdata` 2026.6 is already installed with Django).

**Decisions (human, 2026-11-19):**
- The notice is EXPERIENCE.md "Upload notice (exact text)" word for word. The test checks that every quote the notice shows is in the stored file, and that the human-reviewer, do-not-submit-sensitive and EEA/Switzerland/UK quotes are present. Stored quotes the notice leaves out are not tested.
- A POST with the box ticked stores `notice_ack_at` and `notice_version` at once, even if the file is then rejected; the file error is shown without the notice.
- The README section "AI notice and daily limit" is written in this story, as AC 8 says.

**Never:** change story 2.2's check order or messages; a job queue or AI call; a stored PDF; a file field; counting by deleting-aware queries (deleting a lecture must not lower the count).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Not acknowledged | `notice_ack_at` empty, valid PDF, box not ticked | No Lecture, notice shown | "Tick the box to confirm you have read the notice." (status 400) |
| Acknowledge | box ticked + valid PDF | `notice_ack_at` = now, `notice_version` = current; Lecture created; next upload shows only a short line | none |
| Old version | stored version ≠ current | notice shown again, upload refused until ticked | as row 1 |
| Within limit | 4 accepted uploads today | 5th creates Lecture + one `UploadLog` in one transaction | none |
| Over limit | 5 accepted today (Oslo date) | No Lecture, no AI call | "You have used your 5 uploads for today. You can upload again tomorrow." (number = setting) |
| Rejected file | too big, not PDF, 51 pages, no text | Nothing counted | story 2.2 messages |
| Midnight | 23:59 and 00:01 Oslo with `UPLOADS_PER_DAY=2` | New day starts at local midnight (winter and summer time) | none |

</frozen-after-approval>

## Code Map

- `accounts/models.py` -- `User.notice_ack_at`, `notice_version` already exist; no change, no migration there.
- `lectures/models.py` -- add `UploadLog` (user FK CASCADE, `created_at` UTC, `local_day` date, index on user+local_day) with `UploadLogQuerySet.for_user`; reuse `LectureQuerySet` pattern.
- `lectures/services.py` -- `create_lecture_from_upload`: notice check first (before the temp file), limit check and `UploadLog` insert inside the existing final `atomic()`. Add `acknowledge_notice(user)`, `notice_is_current(user)`, `local_today()` (one clock function, patched in tests), `uploads_left_today(user)`. Do not change the check order or MSG_* texts.
- `lectures/views.py` -- `upload`: read the box, call `acknowledge_notice`, pass `show_notice` and `uploads_left` to the template.
- `lectures/notice.py` (new) -- `NOTICE_VERSION = 1`, notice text constants; the template renders from it so one source feeds page, test and README.
- `templates/lectures/upload.html`, `templates/lectures/_upload_notice.html` (new) -- full notice plus checkbox "I have read this notice about Google's terms."; short line once acknowledged; rule "You can upload N lectures per day. Uploads left today: K".
- `config/settings.py`, `.env.example` -- `UPLOADS_PER_DAY`, `LIMIT_TIME_ZONE`.
- `lectures/migrations/0003_uploadlog.py` -- new migration.
- `lectures/tests.py` -- existing `UploadTests.setUp` acknowledges the notice; new tests below.
- `README.md`, `docs/required_readme_headings.txt` -- "AI notice and daily limit".
- Do not touch: `core/pdf_text.py`, `core/extract_cli.py`, `lectures/upload_handlers.py`.

## Tasks & Acceptance

**Execution:**
- [ ] `lectures/models.py` + `0003_uploadlog.py` -- `UploadLog` with owner-scoped `for_user`
- [ ] `lectures/notice.py`, `templates/lectures/_upload_notice.html`, `upload.html` -- exact notice, checkbox, short line, uploads left
- [ ] `lectures/services.py`, `lectures/views.py` -- acknowledgement gate, version check, count + insert in one transaction, limit message
- [ ] `config/settings.py`, `.env.example` -- the two settings with validation
- [ ] `lectures/tests.py` -- `test_fr6_upload_refused_without_acknowledgement`, `test_fr6_notice_contains_stored_google_quotes`, `test_fr6_new_notice_version_requires_new_acknowledgement`, `test_fr7_sixth_upload_rejected`, `test_fr7_rejected_files_do_not_count`, `test_fr7_day_boundary_uses_oslo_time` (fixed clock), setting = 2, `UploadLog` other-user 404, no temp file left after notice and limit refusals, no AI import
- [ ] `README.md`, headings file, `test_readme_has_required_sections` -- new section

**Acceptance Criteria:**
- Given the story ACs 1-8, when `.venv/Scripts/python manage.py test` runs, then all pass and `makemigrations --check` reports no changes.
- Given a refusal for notice or limit, when it ends, then no Lecture, PageText or UploadLog row and no temp file remain.

## Implementation Notes

Implemented directly (no coding subagent; none was requested). New: `lectures/notice.py` (one source for the notice, `NOTICE_VERSION = 1`), `UploadLog` + migration `0003`, `_upload_notice.html`. The existing upload tests now acknowledge the notice in `setUp`. README section is generated from `notice.py` and a test compares it with the quotes. No package installed; the test server was never started (Django test client only). `LimitSettingsTests` starts a child Python to prove a bad `UPLOADS_PER_DAY` or `LIMIT_TIME_ZONE` stops startup. Full suite: 83 tests pass (after the first build); `makemigrations --check` clean. One slip: the plan edit at approval ran with the system `python`, not `.venv/Scripts/python`.

## Plan Change Log

- 2026-11-19, human decision at approval (open question 1A): the notice follows EXPERIENCE.md instead of AC 3's "every stored quote". Reason: a short, plain notice is better for the primary user (second-language students), and the quotes left out mainly concern the developer (for example Use Restrictions). `gemini-terms-checked-2026-10-17.md` stays unchanged as the source of the quotes.

## Review Triage Log

Quick lens, done by me against the diff (no reviewer subagent was started, since none was requested). 0 findings kept.
- low / rejected -- the over-10 MB path shows the size message before the notice check; the notice is still shown on that page and the upload is refused either way.
- false -- "ack stored for a bad file lets a user skip reading": decided by the human (question 2A).
- false -- "limit check after extraction wastes work": AD-20 order, story 2.2's order must not change; no AI call happens.

Second review (2026-11-19), asked for by the human: reviewer subagent on the full diff, with focus on UploadLog owner scoping, limit bypass and the notice wording. Answers: UploadLog goes through `for_user` only and no view reads it by id; 15 concurrent uploads at limit 5 gave exactly 5 accepted (throwaway SQLite file, IMMEDIATE + atomic holds); no bypass found. 6 findings, triaged by me:
- low / patch -- extra visible heading "Before you upload" in the notice, not in EXPERIENCE.md. Fixed: heading removed, `aria-label` on the section.
- low / decision -- "(link)" in EXPERIENCE.md became a real link. Human chose A: the link replaces "(link)"; the test allows exactly this difference.
- low / patch -- whole "Unpaid quota ("Unpaid Services"):" line was bold; EXPERIENCE.md bolds only "Unpaid quota". Fixed in the template and in the README.
- medium / patch -- `test_fr6_notice_text_matches_experience_md` did not check the Unpaid heading, the terms line or bold words, and never read the rendered page. Fixed: it now compares the rendered notice with EXPERIENCE.md text and bold words. Checked by putting each of the three differences back: the test fails each time.
- false / rejected -- limit checked after extraction (up to 20 s per valid PDF for a user at the limit): AD-20 order; story 2.2's order must not change; no AI call or storage.
- low / defer -- changing `LIMIT_TIME_ZONE` on a running app can allow or block one upload; written to deferred-work.md.
- not a finding -- `SHORT_LINE` is Recall's own wording, not in EXPERIENCE.md; kept.

## Design Notes

- Why the limit check sits after extraction: AD-20 step 5 follows step 4, and story 2.2's order must not change. A user at the limit who uploads a bad file sees the file error; the limit is checked on a valid file, still with no AI call.
- Why `atomic()` is enough: the database uses `transaction_mode: IMMEDIATE` (AD-24), so the count and insert cannot interleave with another upload by the same user.
- `local_day = utc_now.astimezone(ZoneInfo(LIMIT_TIME_ZONE)).date()`; `UploadLog` is never deleted with a lecture (no FK to Lecture), so deleting lectures cannot reduce the count.

## Verification

**Commands:**
- `.venv/Scripts/python manage.py test` -- expected: all tests pass
- `.venv/Scripts/python manage.py makemigrations --check` -- expected: no changes

**Manual checks (if no CLI):**
- Start `.venv/Scripts/python run.py --port 8001`, upload as a new user with and without the tick, then stop the server.
