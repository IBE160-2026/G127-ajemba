# Review: architecture-recall.md against the good-spine checklist

Reviewed: `architecture-recall/architecture-recall.md` (draft, 16 ADs) against `prd-recall.md` (final) and `ux-recall/EXPERIENCE.md` (final). Read-only review; no existing file was changed. Date: 2026-10-17.

## Verdict

A strong, readable spine. The paradigm, the wrapper modules, versioned prompts and the two-step evaluation are well decided. But the data model (AD-8, ER diagram) is too thin for the quiz-progress, essay-resubmit and Demo Mode requirements, so two units could build incompatible persistence. Several rules are not enforceable as written, and the "verified-current" tech check is not met (every package is "latest, pin at install"). Fix the Critical and High items before epics are cut.

## Checklist scorecard

| Checklist item | Result |
| --- | --- |
| Fixes the real divergence points, misses none | Partly. Misses: quiz/essay progress storage, Attempt/EssaySubmission relation, Demo Mode scope, upload-to-worker handoff, language field, htmx focus handling |
| Every AD Rule enforceable and prevents its divergence | Partly. AD-2, AD-4, AD-8.2 and AD-5.5/5.6 have no enforcement mechanism or are vague |
| Deferred items cannot cause divergence | Mostly. Gemini limits and the django-q2 job test do affect AD-3/AD-4 (see M-7, H-4) |
| Named tech verified-current | No. No pinned versions and no verification date; only Django 5.2 LTS is concrete |
| Every FR/SM covered by an AD or the map | Partly. SM-1, SM-C1..C3 and FR-31 have no mechanism; FR-6 and FR-11 have no enforceable rule |
| Dimensions decided, deferred or open | Deployment, provider, operations, data, testing: mostly. Security: thin (see H-7, M-6) |

---

## Critical

### C-1. AD-8 / ER diagram: no home for quiz progress, essay drafts or an in-progress Attempt
- **Wrong:** PRD §6.6 and EXPERIENCE (Interaction Primitives, Essay behaviour) require current question, answers given and essay text to be stored with the account, resumed after tab switch, reload or leaving, and "Start again" to open a new Attempt. AD-8 lists eight tables and none holds the current question, an "in progress / finished" Attempt state, or an essay draft. AD-11 says the draft is "saved" but not where. One unit will add columns on `Attempt`, another a new table.
- **Fix:** Extend AD-8: `Attempt` has `quiz_type`, `status (in_progress|finished)`, `current_index`, `started_at`, `finished_at`; invariant "at most one in-progress Attempt per user, lecture and quiz type; Start again finishes or abandons it and creates a new one". `Answer` holds chosen option or typed text, `skipped`, and stored `is_correct`. Essay drafts are a field on a draft row or on `EssaySubmission` with `status draft|submitted`, keyed by Attempt and Question.

### C-2. AD-8 / ER: `EssaySubmission` is not linked to `Attempt`; the 3-submission rule has no AD
- **Wrong:** The ER diagram links `EssaySubmission` only to `Question`. PRD FR-17/FR-18/FR-19 and EXPERIENCE define up to 3 submissions per Essay per Attempt, last counts, all shown on Results. Nothing says who enforces the maximum of 3 (server side, not just a disabled button), how "last counts" is queried, or that the row reaches its user (AD-8.2 requires an FK path). The 3-per-Essay cap also guards AI cost (§6.2) yet appears in no Rule.
- **Fix:** Add `EssaySubmission.attempt` FK, `sequence` (1..3, unique with attempt and question), stored feedback text, and covered key-point indices. Add to AD-8/AD-5: "the service rejects a 4th submission; a DB unique constraint on (attempt, question, sequence)". Add the Attempt-to-EssaySubmission edge in the ER diagram.

### C-3. AD-8.6 vs FR-3/FR-4/FR-5: upload-to-worker handoff is contradictory
- **Wrong:** "The original PDF is not kept; only per-page text is stored." But FR-3/FR-4 rejections must appear immediately on the Upload page with nothing created (EXPERIENCE, Upload rejected), which implies extraction runs inside the request. Yet the Processing screen's first step is "Reading your PDF", which implies extraction in the job. If extraction is in the job, the PDF must be stored temporarily; if in the request, a 50-page pdfplumber run happens in the web process and eats the 120 s budget. Two units will pick differently.
- **Fix:** Decide in AD-3 or AD-9: validation and extraction run synchronously in the upload view (page count, size, content-type, 100 chars/page), per-page text is saved, and only then is the job queued with the lecture ID. The PDF bytes are never written to disk. Re-label the first Processing step honestly (see H-2).

---

## High

### H-1. AD-10 / AD-4: "Demo Mode" has no defined scope (global flag vs session)
- **Wrong:** AD-10.2 says demo mode starts when no key is set, and "Try the demo" is always available (even with a key). AD-10.3 says "in demo mode `ai_client` never calls out", but AD-4 defines no-call only for "no key". With a key set and a user who clicked the demo, how does `ai_client` or the banner know the request is demo? Also unspecified: with no key, can users still register and see an empty app; what does Upload show (EXPERIENCE says "Processing needs an API key" with a README link).
- **Fix:** Define one function `is_demo(request)` in one module: true if no key, or the current lecture is `is_example`. Rule: the decision to call out is made from the Lecture row (`is_example` never calls out) plus the key, not from a global mode. The banner and the upload guard use the same function.

### H-2. AD-5 vs FR-5 / EXPERIENCE (Processing): "real steps" cannot be real with one AI call
- **Wrong:** PRD FR-5 requires "real steps, not a made-up percentage". EXPERIENCE shows three steps (Reading your PDF, Finding the key points, Writing the summary). AD-5 says one call produces the whole Summary, and AD-8.5 gives `Lecture.status` only `processing`. Steps 2 and 3 would be invented.
- **Fix:** Add `Lecture.step` (`reading|generating|saving`) set via `set_status()`, and either tell the UX to show only real steps (for example "Reading your PDF", "Making the summary", "Checking the result") or record in the spine that steps 2 and 3 map to the generate and validate phases. Record the decision as a PRD/UX follow-up.

### H-3. AD-8.1: table list is incomplete and its JSON rule contradicts itself
- **Wrong:** (a) "Tables:" is stated as the whole set, but needs more: the FR-6 acknowledgement (field on user or a table), the FR-7 upload-count table (named in AD-15 but not in AD-8), the AI usage log (AD-4/AD-5.7, table or file?), prepared Demo essay answers with stored feedback (FR-23), and a quiz-status location (per-type statuses live on `Lecture`? not stated). (b) JSON is allowed "only for multiple-choice options and essay key points", yet Source References are "lists of integers" on `SummaryPart`, `Question` and each key point, which also need JSON or a child table. (c) Rule 3 says content is "immutable" but also "a retry replaces the whole result"; replacing Questions would orphan Answers and Reports.
- **Fix:** Rewrite the table list as complete (add `UploadEvent`, `AiCallLog` or log-file decision, `PreparedAnswer`, ack fields). Allow JSON for "options, key points and source references" explicitly. State that a retry only applies to a quiz whose status is `failed` (no Questions exist yet), so replacement never orphans rows.

### H-4. AD-3: no timeout/retry/time budget; the 120 s target is not protected
- **Wrong:** FR-8/SM-1 allow 60 s (up to 30 pages) and 120 s (31 to 50 pages). django-q2's default redelivery (`retry`, about 60 s) can re-queue a task that is still running, which is exactly the "duplicate run, double cost" AD-3 claims to prevent; `timeout` and `retry` are not set. AD-4 allows unbounded "wait and retry on rate limit" plus 2 retries on unusable output, so worst case is 3 calls plus waits, far over 120 s. No per-call HTTP timeout is stated. One worker means a Summary job (up to 120 s) blocks quiz generation (FR-12 to FR-16, 60 s each) and essay feedback for everyone. The fallback if the django-q2 job test fails is not named even though it is Deferred.
- **Fix:** AD-3: set `timeout` greater than the longest call chain, `retry` greater than `timeout`, and `max_attempts=1` with app-level retries only. AD-4: per-call timeout, a total wall-clock budget per job, and a cap on rate-limit waiting after which the job fails with the plain message. Decide whether essay feedback runs inline (synchronous in the request with a timeout) or in the queue, and whether a second worker is allowed. Name the fallback (for example a plain management-command worker loop) in Deferred.

### H-5. AD-1 vs AD-11 / EXPERIENCE: "htmx only" contradicts required JavaScript
- **Wrong:** AD-1 says "interactivity is htmx only" and "no JavaScript framework". But the text size control (instant, remembered on the device), the `localStorage` essay backup with newer-wins comparison, tab-to-focus behaviour and skip-link focus all need small custom JavaScript. No AD says where it lives or how it is bounded. Two units will each add inline scripts.
- **Fix:** Amend AD-1: "htmx plus one hand-written `static/js/app.js` (no framework, no build step) for text size, essay backup and focus helpers; no inline scripts". Add the file to the structural seed, with `static/` and `templates/`.

### H-6. No AD governs htmx partial swaps, per-tab URLs, focus and live regions
- **Wrong:** EXPERIENCE requires a distinct page address per tab (`/lectures/12/summary`), working Back button and refresh, unique page titles that update, focus moved to the result line after "Check answer", focus kept on polled status changes, polite live regions, and no animation under reduced motion. These cross every screen. AD-1 only lists what htmx "covers". Each unit will choose full-page vs partial rendering and its own focus handling.
- **Fix:** Add an AD (or Consistency Convention): every URL renders a full page and, when `HX-Request` is present, returns only the partial; tab navigation uses `hx-push-url` and updates the `<title>`; one shared template macro handles `hx-swap`, focus target and live region per component class (feedback card, status row, essay feedback).

### H-7. Security and privacy gaps in AD-3 / AD-11 / conventions
- **Wrong:** (a) django-q2 stores task arguments and results in the database; if page text is passed as an argument, lecture text outlives "delete removes everything" (FR-21) and breaks the "no lecture text in logs" spirit. (b) AI output is rendered into templates and swapped by htmx; nothing forbids `|safe` or markdown-to-HTML, so injected markup from a hostile slide could reach the page (AD-5 only covers prompt injection). (c) The `localStorage` backup is cleared only on logout; on a shared computer where the session simply expires, the next person sees a previous user's draft. Newer-wins needs a comparable revision, but client and server clocks differ. (d) Session store for Demo attempts is unspecified (cookie-signed sessions have a 4 KB limit).
- **Fix:** AD-3: jobs take IDs only; set django-q2 `save_limit`/result retention to a minimum and purge on lecture delete. AD-5.4: output is autoescaped plain text; `|safe` is forbidden (add a test that greps templates). AD-11: key the backup by user ID, lecture and question; use a server-issued revision counter instead of timestamps; set `SESSION_ENGINE` to the database backend.

---

## Medium

### M-1. AD-2: Rule is not mechanically enforceable
- **Wrong:** "Views read the request, call one service"; "pure modules import no models/request/network"; "only module that imports X". Nothing checks these. AD-14 has no architecture test. The tree lists only `core/scoring.py`, but AD-2 names four pure modules (scoring, answer matching, Review List, AI-output validation), so their file names are also a divergence point.
- **Fix:** AD-14: add an import-boundary test (parse imports: `google.genai` only in `ai_client.py`, `pdfplumber` only in `pdf_text.py`, no `django.db`/`django.http` in pure modules, no model-name string in code). Name the modules in the seed: `scoring.py`, `matching.py`, `review_list.py`, `validation.py`.

### M-2. AD-8.2: ownership rule has no single enforcement point
- **Wrong:** "Every query goes through the owner" is a convention. FR-2 and SM-7 need it for every view, plus the Example Lecture exception (user NULL, readable by anyone). Report (FR-22) says it stores the User, but Demo visitors are anonymous.
- **Fix:** One helper, for example `get_lecture_for(user, id)`, is the only way views fetch lectures/attempts (returns 404 for others; includes the `is_example` exception in one place). AD-14: a test walks the URLconf and hits every route as another user and as anonymous. Decide: reports on the Example Lecture are rejected or stored with a null user.

### M-3. AD-8: Report cascade destroys regression evidence; delete during processing
- **Wrong:** "Deleting a lecture removes everything" cascades to `Report`, so a reported question disappears before the builder reviews it (FR-31). Also a worker may still run for a lecture deleted mid-processing.
- **Fix:** Store the question text and reason in `Report` as a snapshot with `SET_NULL` on the Question FK, or export reports before delete. AD-3: jobs must check the lecture still exists and stop quietly.

### M-4. AD-3 / AD-8.5: status transitions and recovery not specified
- **Wrong:** `set_status()` is named but not its rules. Missing: the transition table (including `failed -> processing` on retry), atomic compare-and-set (two tabs opening the same quiz must not start two generations), and recovery when `python run.py` is stopped mid-job (a lecture stuck in `processing` forever, contradicting FR-5).
- **Fix:** State the transition table, make `set_status(obj, from_, to)` a conditional `UPDATE ... WHERE status=from_`, and add a startup sweep in `run.py` that marks stale `processing`/`making` rows as `failed`.

### M-5. AD-5 / AD-8: essay rating and the questions-to-Summary-Part link are underspecified
- **Wrong:** The Essay Rating is a count of covered Reference Key Points (glossary), and the Review List needs the missing ones. No AD says the AI returns covered key-point indices (not a number) and that the rating is computed in pure code from validated indices; this also matters for PRD open question 7. The Questions call must also receive Summary Part identifiers to link questions to parts (FR-12/14/16), but AD-5 does not say how.
- **Fix:** AD-5: essay feedback schema returns `covered: [key point indices]`; `scoring` derives rating and missing points; validation rejects out-of-range indices. Questions are generated with the stored Summary Parts (with IDs) in the prompt; the model returns `part_id`, validated against existing parts.

### M-6. AD-16 / FR-6: acknowledgement and notice are not enforced by any Rule; claim about Google terms is unverified
- **Wrong:** FR-6's testable consequence is "no acknowledgement, no upload". AD-16 only requires wording. No AD stores the acknowledgement or enforces it on the server. AD-16 states a fact about Google's free-tier data use without a source or date; those terms differ by region and change, and the builder is in Norway (EEA). AD-16 also lacks the `[ADOPTED]` tag every other AD has. The PRD says "shown once" while EXPERIENCE shows a checkbox on Upload.
- **Fix:** Rule: store `notice_ack_at` and `notice_version` on the user; the upload service refuses without it; a test asserts the notice contains "Google" and "improve its products". Add the source and date checked for the terms claim. Add the tag.

### M-7. Deferred: Gemini limits and model could change AD-3/AD-4/AD-13
- **Wrong:** "Exact Gemini model and its limits" is Deferred, but requests per minute and per day decide the one-worker choice, the pacing in AD-13 and whether the evaluation fits: roughly 6 answers x 3 runs x 2 essays x 3 to 5 lectures is 108 to 180 essay calls, plus summaries and quizzes. A crash midway wastes quota. AD-13 has no resume.
- **Fix:** Add to AD-13: results are cached per (lecture, task, prompt fingerprint, run number) so an interrupted evaluation resumes. Move "check the current free-tier limits" to a dated item, with a note that daily limits can force a multi-day evaluation.

### M-8. Coverage gaps: SM-1, SM-C1..C3, FR-28 report contents, FR-31, FR-11
- **Wrong:** SM-1 (timing measured with the real AI) is bound by no AD; AD-5.7 logs wait time but no evaluation field reports it. AD-13's review sheet omits Question grounding (90 %), plain-language and wording checks (FR-10), and the counter-metrics: duplicate/wrong question counts (SM-C1), difficulty comparison (SM-C2), Summary length next to coverage (SM-C3). FR-31 (builder lists reports) has no mechanism; PRD says no admin screen but Django admin is a free decision that is not made. FR-11's AI notice has no rule.
- **Fix:** AD-13: the report includes elapsed time per Lecture (SM-1), Summary length and coverage (SM-C3), duplicate/unclear count (SM-C1), and a difficulty note (SM-C2); add grounding and wording checkboxes. Add `manage.py export_reports` or enable Django admin read-only and say so. Add the AI notice to the shared Summary/Quiz base template as a convention.

### M-9. Language of the Summary is not modelled
- **Wrong:** EXPERIENCE requires `lang="en"` or `lang="nb"` on summary and question text, and PRD §4.3 says output follows the slide language. No AD adds `Lecture.language`, says who detects it (model output, validated to `en|nb`), or tells prompts to answer in the slides' language.
- **Fix:** AD-8: `Lecture.language` in {en, nb}, returned by the Summary call and validated. AD-6: prompts instruct "write in the language of the slides".

### M-10. AD-12: DEBUG default can break "fresh clone starts in Demo Mode"
- **Wrong:** With no `.env`, "a missing SECRET_KEY stops with a clear message when DEBUG is off". DEBUG's default is not stated. If it defaults to off, a fresh clone cannot start without creating `.env`, contradicting the same AD ("app starts with no `.env`") and SM-9/FR-24. Related: how example data loads "on first run with no manual step" (migrate signal? `run.py`?), and whether `run.py` runs `migrate`, is unspecified.
- **Fix:** Default `DEBUG=True` for local runs, and make `run.py` do `migrate` plus idempotent example load (keyed by a version in `example_lecture.json`). State that `run.py` uses `runserver --noreload` (the autoreloader would double-start the worker).

### M-11. Vague numeric rules are not enforceable
- **Wrong:** AD-5.5 "far over a safe size", AD-5.6 "about 3,000 characters", AD-11 "about 3 seconds / 2 seconds". Question counts 10/8/2 (PRD open question 5, still tuning) appear in no AD, so prompt and validator can disagree. Report reason limit (300, EXPERIENCE) is also absent.
- **Fix:** Name settings with exact defaults: `MAX_PROMPT_CHARS`, `ESSAY_MAX_CHARS=3000`, `POLL_SECONDS=3`, `DRAFT_SAVE_MS=2000`, `N_MC=10`, `N_FILL=8`, `N_ESSAY=2`, `REPORT_MAX_CHARS=300`; prompts and validators both read these.

### M-12. Text normalisation and Source Reference display not centralised
- **Wrong:** FR-4 (characters per page), FR-9 (key term appears in text), FR-15 (answer matching) and the chips ("Slides 12 to 15") all depend on normalisation and formatting rules. PDF text has ligatures, hyphenation and line breaks; Norwegian letters need Unicode normalisation and case folding. Source References are stored as integer lists, but the chip text for a non-contiguous list such as [3, 7, 8] is not defined.
- **Fix:** One pure `text_utils.normalise()` used by FR-4, FR-9 and FR-15 (NFC, casefold, collapse whitespace), and one pure `format_slides()` for chips. Add the module names to the seed.

---

## Low

### L-1. Stack: nothing is verified-current
- **Wrong:** Python "3.12 or newer" is unbounded (newer versions may not be supported by Django 5.2 or the packages). Django 5.2 LTS is a sound choice, but there is no patch number, no verification date and no check that django-q2 supports it; every other package is "latest stable, pin at install". Gemini model names are deprecated often; AD-4 correctly keeps the name a setting but there is no dated check.
- **Fix:** Add a dated "Verified on" column to the Stack table with concrete versions (Python 3.12 or 3.13; Django 5.2.x; django-q2 x.y; pdfplumber; google-genai; django-environ; htmx 2.0.x), and a supported Python range. Keep "pin at install" only for the job test.

### L-2. Seed and file names
- **Wrong:** The tree has no `static/`, `templates/`, `logs/`, `.gitignore` or the location of `manage.py evaluate` (a management command must live in an app, for example `lectures/management/commands/evaluate.py`; `evaluation/` is data only). The SQLite file name and location are not stated. The fingerprint registry for AD-6 (where the last-seen prompt fingerprint is kept) is not located. The "replay" in the structural seed shows `example_lecture.json`, while AD-14 uses separate stored sample responses; whether these share one lookup interface is unclear.
- **Fix:** Add these paths to the seed, and define replay as one lookup interface keyed by (task, ids) with two data sources (demo data, test fixtures).

### L-3. AD-15: deployment and operations checklist
- **Wrong:** The "if you deploy this" list omits a production WSGI server (Gunicorn does not run on Windows; Waitress does), static files (WhiteNoise), and the django-q2 single-worker constraint on a host. The `.env`-tracked-by-git test (AD-12) needs the git CLI and fails in a zip export. Upload counting says "per calendar day" without a time zone (UTC vs Norway local time), and it is undefined whether "Try again" on a failed lecture counts as a new upload.
- **Fix:** Add the items to the README list; make the git test skip if there is no `.git`; add `UPLOAD_DAY_TZ=Europe/Oslo` and state that retries of a failed lecture do not count.

### L-4. Minor internal consistency
- **Wrong:** AD-8 "Binds" ends with FR-21 out of order; AD-1/AD-12 mention `.memlog` indirectly but the sources list does not include `.memlog.md`; AD-3 "Pin django-q2 after a job test" appears in both the Rule and Deferred (duplicate source of truth); AD-9's "keep whichever gives cleaner text" has no criterion; capability map lists FR-22 only under "Saved lectures, delete, report" with AD-8, but no rule covers the 300-character reason or the confirmation.
- **Fix:** Tidy ordering, single-source the django-q2 test, and give AD-9 a criterion (for example fewer than N broken-word lines on the sample PDF).

---

## Consistency with PRD / EXPERIENCE: quick table

| Topic | Spine | PRD / EXPERIENCE | Status |
| --- | --- | --- | --- |
| Demo Mode always-available button, no-key start | AD-10.2 | FR-23 | Consistent, but scope undefined (H-1) |
| Demo attempts in browser session | AD-10.4, AD-11 | FR-2, §6.6 | Consistent; session engine unspecified (H-7) |
| Quiz progress with the account | AD-11 (answers saved) | §6.6, EXPERIENCE | Partly; no storage model (C-1) |
| Essay: 3 submissions, last counts | AD-5 cost only | FR-17..19 | Not enforced (C-2) |
| 120 s for 31 to 50 pages | Not mentioned | FR-8, SM-1 | Not protected (H-4, M-8) |
| Upload limits 50 pages / 10 MB / daily 5 | AD-15, conventions | FR-3, FR-4, FR-7 | Consistent; time zone open (L-3) |
| Real processing steps | AD-5 one call | FR-5 | Conflict (H-2) |
| Gemini free-tier notice | AD-16 | FR-6, EXPERIENCE | Wording aligned; enforcement missing (M-6) |
| Django version | 5.2 LTS (Stack only) | n/a | Consistent inside the spine; not verified (L-1) |
| File names | `core/scoring.py` only | n/a | Pure modules unnamed (M-1) |
| Counts of ADs | 16 in text | n/a | Consistent; AD-16 lacks tag (M-6) |
