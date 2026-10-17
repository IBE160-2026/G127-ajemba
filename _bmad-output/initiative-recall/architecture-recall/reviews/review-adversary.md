# Adversarial Review - Architecture Spine "Recall"

Target: `architecture-recall/architecture-recall.md` (AD-1..AD-16, conventions, seed). Siblings read: `prd-recall.md`, `EXPERIENCE.md`.
Method: for each finding, two units one level down (two AI-assisted coding sessions, each building a story) that both comply with every AD to the letter, and the point where the result is incompatible. Severity: B = blocks the build or breaks a stated PRD/SM outcome, H = likely defect or leak, M = real but containable.

## Verdict

The spine is strong on layering (AD-2) and on what is forbidden (providers, secrets, JSON misuse). It is weak on the thing it exists to do: **fixing the shared shapes and the single owner of each state change.** Concretely:

1. The data model (AD-8) lists 8 tables but the spine itself needs at least 5 more entities or fields it never names (page text, upload log, draft/progress, per-quiz status, essay-submission status, AI usage log, prepared answers). Each will be invented twice.
2. `set_status()` is a name, not a contract. Nothing says what it compares, who may call it, or what happens on crash.
3. django-q2 defaults (60 s task timeout, retry re-queue, persisted task args/results) silently contradict AD-3, AD-5, AD-8 and AD-15.
4. The fresh-clone path has at least four independent ways to fail (placeholder key, DEBUG default, CRLF fingerprints, static files).
5. Security rules are stated as intentions ("every query goes through the owner") with no mechanism that two sessions would implement the same way.

Do not start stories until the 9 "must-fix" ADs in the last section are added. Roughly 20 findings follow.

---

## A. Data shapes and ownership

### F-1 (B) Page text, upload log, drafts, progress and per-quiz status have no owner
- **Units:** U1 "upload + processing job" and U2 "essay tab + draft saving" and U3 "daily limit".
- **ADs both obey:** AD-8.1 (tables listed; JSON only for MC options and essay key points), AD-8.6 ("only per-page text is stored"), AD-11 (draft saved on server), AD-15 (limit counted "from a database table"), AD-8.5 (each quiz type has its own status).
- **Divergence:** AD-8.1 closes the table list, yet AD-8.6, AD-11, AD-15 and AD-8.5 each require storage that is not in it. U1 stores page text as a `Lecture.pages` TextField joined with form feeds; another session uses a `Page` table. U2 stores the draft in `EssaySubmission` with `status=draft`; a second session adds `Answer.draft_text`; a third uses `Attempt.state` JSON (forbidden by 8.1 but only "JSON fields are used only for..." - a TextField holding JSON passes the letter). U3 counts `Lecture` rows per day, so deleting a lecture resets the limit; another creates `UploadLog`. Quiz status becomes three columns on `Lecture` in one story and a `Quiz` table in another (the ER diagram has no Quiz entity; the glossary does).
- **Fix (new AD-17 "Complete entity list"):** extend AD-8.1 to the full table list with owners and columns: `Lecture(user null, is_example, status, status_changed_at, notice fields)`, `PageText(lecture, number, text)`, `Quiz(lecture, type, status, status_changed_at, unique(lecture,type))`, `Attempt(user null, lecture, quiz, started_at, finished_at null)`, `Answer(attempt, question, value, is_correct, is_skipped, unique(attempt,question))`, `EssayDraft(attempt, question, text, version)`, `EssaySubmission(attempt, question, seq, text, status, rating, covered, feedback)`, `UploadLog(user, created_at_utc, local_day)`, `AiCallLog`, `Report`. State "no other tables; django-q2 tables are infrastructure only".

### F-2 (B) Source Reference stored two ways, and "slide numbers" rendered two ways
- **Units:** U1 (summary generation) and U2 (quiz generation); U3 (source chip rendering).
- **ADs:** AD-8.4 "lists of integers", Conventions "Source References are lists of integers", AD-8.1 JSON only inside Question.
- **Divergence:** SummaryPart has no allowed JSON field, so U1 stores `"12,13,14,15"` in a CharField, U2 stores a JSON list in `Question`. The chip renderer U3 prints "Slides 12 to 15" from a list. A noncontiguous reference `[3, 7, 12]` is printed "3 to 12" by one, "3, 7, 12" by another. A third session stores range endpoints `[12, 15]`, which is also "a list of integers" and passes the page-count check. Essay Reference Key Points also carry Source References (FR-16), nested inside the allowed JSON, which is a second shape again.
- **Fix:** AD-8.4 add: "canonical form is the sorted, de-duplicated list of every slide number (never endpoints). One shared type `SourceRef` in `core/types.py`, one parser/serializer, one formatter `format_slides(refs)` that collapses only runs of 3 or more consecutive numbers. SummaryPart and Question store it via the same custom field." Extend the JSON exception to name this field.

### F-3 (B) Pure modules have no agreed input shapes
- **Units:** U1 (results view builds Review List for one Attempt), U2 (saved-lectures list "past attempts: date, quiz, score").
- **ADs:** AD-2.2 pure modules import no models; AD-8.
- **Divergence:** since pure code cannot import models, each caller invents its adapter: dicts vs namedtuples vs separate lists of `(question_id, correct)`. U1 treats a skipped or unvisited question as wrong; U2 computes the score as `sum(is_correct)` over existing Answer rows only, so an abandoned or partly skipped attempt shows a higher score than the results page. FR-13 (unanswered = wrong) and FR-19 are then implemented twice.
- **Fix:** AD-2 add: "Pure modules take and return frozen dataclasses defined in `core/types.py` (`AnswerRecord`, `QuestionRecord`, `AttemptResult`). Score and Review List have exactly one entry function each; no view or service may compute a score itself. The denominator is the number of questions in the quiz, not the number of Answer rows."

### F-4 (H) Essay submission counting, "last counts", and who owns Essay Rating
- **Units:** U1 (essay feedback endpoint), U2 (results tab), U3 (review list).
- **ADs:** AD-8 (EssaySubmission table exists; `QUESTION ||--o{ ESSAYSUBMISSION` in the ER, no link to Attempt), AD-3 (job idempotency "stop if result stored"), AD-8.3 (immutable).
- **Divergence:** The PRD limit is 3 submissions per Essay per **Attempt**, but the ER ties the submission to Question only. U1 counts per question for the user (so "Start again" never resets, contradicting FR-17); another counts per attempt. "Last" is `max(id)` in one, `max(created_at)` in another (UTC second resolution tie on a double-click). Double click or two tabs at count = 2 both pass the check and create submission 3 and 4; SQLite gives no `select_for_update`. A failed AI call either consumes an attempt or not, depending on the session. Essay Rating is stored by U1 as an integer, derived by U2 from `covered` list, and U3 reads `covered` for missing points: three sources of truth. Whether the feedback job is in-request (rate-limit sleep, see F-9) or a queued job is also open: AD-3 binds FR-17 to the queue, EXPERIENCE ("Reading your answer...") does not say.
- **Fix:** AD-8 add: `EssaySubmission(attempt, question, seq)` with `UNIQUE(attempt, question, seq)` and `seq <= 3` check; seq assigned inside one `BEGIN IMMEDIATE` transaction; "last" = highest `seq`; a submission whose AI call failed has `status=failed` and does not count toward 3 (but counts toward a cost cap, see F-15); `rating` is derived by one pure function from `covered` and never stored. Essay feedback is a queued job with its own status field set via `set_status()`.

### F-5 (H) Two owners of AI-output validation, so retries do not cover grounding
- **Units:** U1 (`ai_client` summary call), U2 (summary service).
- **ADs:** AD-4 ("`ai_client.py` owns ... validation of the result, 2 retries"), AD-2.2 (AI-output validation is a pure module), AD-8.4 (checked against the page count "before saving"), AD-5.4.
- **Divergence:** U1 validates schema inside `ai_client` and retries twice. Grounding checks (slide numbers exist, key terms appear in text, every Question links to a Summary Part) need the page text and Summary Part ids, so U2 runs them in the service after the call returns. A grounding failure then happens outside the retry loop: FR-27 says retried twice, but the user sees an immediate failure on the first bad slide number. Or U1 passes the whole lecture into `ai_client` to validate, and `ai_client` now depends on lecture shapes.
- **Fix:** AD-4/AD-2: "the pure validator `validate_*(output, context)` is called by `ai_client` inside its retry loop; the caller passes `context` (page count, page text, summary part ids). The retry budget is 2 extra attempts total per logical call, shared by schema and grounding failures. No other layer retries AI calls."

### F-6 (H) Two normalisers for text: key-term grounding vs fill-in-the-gaps matching
- **Units:** U1 (FR-27 key term must appear in the lecture text), U2 (FR-15 answer matching).
- **ADs:** AD-2.2 both pure; Conventions silent on text normalisation.
- **Divergence:** PowerPoint-exported PDFs yield ligatures (ﬁ, ﬂ), soft hyphens, line breaks mid-term, NFD vs NFC for å/ø/æ. U1 does `term.lower() in text.lower()`: valid terms fail, produce three failed retries (F-5) and a "Failed" summary for any lecture with "classiﬁcation". U2 strips/lowercases only per FR-15. A student types "klassifisering" and the expected answer, taken from the page text, contains the ligature, so the match fails although the rule says edit distance 1 is accepted.
- **Fix:** Conventions add: "one function `normalize_text()` (Unicode NFKC, casefold, collapse whitespace, remove soft hyphens, re-join hyphenated line breaks) is applied by `pdf_text.extract_pages` output cleaning, by grounding checks, and by answer matching. Edit distance is computed on the normalised strings."

### F-7 (M) Slide numbering broken by failing pages
- **Units:** U1 (`pdf_text`), U2 (marker builder in `ai_client`).
- **ADs:** AD-9 "index + 1 is the slide number", Conventions.
- **Divergence:** pdfplumber raises on a corrupt page, or the code skips pages with empty text. A session that filters empties shifts every later slide number and every Source Reference is off by one while still "valid" against the page count. FR-4's average-characters test also depends on whether empty pages count in the denominator.
- **Fix:** AD-9 add: "`extract_pages` always returns exactly `len(pdf.pages)` strings, empty string for an unreadable or image-only page. Never filter. Average characters per page is computed over all pages."

---

## B. State mutation and concurrency

### F-8 (B) `set_status()` is a name, not a contract; stuck "Processing" is unrecoverable
- **Units:** U1 (web view for "Try again" / delete / quiz-first-open), U2 (worker job).
- **ADs:** AD-3 (status only through `set_status()`; jobs safe to run twice), AD-8.5 (state machines), AD-8.3.
- **Divergence:** The machine in AD-8.5 lists forward edges only, and `failed -> processing` (retry) is not an edge. Neither session is told to compare-and-set. U1's retry view reads `status == failed`, then calls `set_status(processing)` and enqueues; a double click enqueues two jobs. U2's job at start calls `set_status(processing)` unconditionally, overwriting a `failed` that U1's reaper wrote. If the worker process is killed (Ctrl+C in `run.py`, laptop sleep, the 60 s django-q2 timeout, see F-10) the row stays `processing` forever: FR-5 "Processing..." with no exit and no timeout. The same applies to the three quiz statuses. Also enqueueing inside the request transaction lets the worker run before the row commits.
- **Fix (new AD):** "`set_status(obj, from_states, to_state)` is a conditional UPDATE (`WHERE status IN from_states`) returning whether it changed anything; callers abort on False. Allowed edges are listed: `uploaded->processing`, `processing->ready|failed`, `failed->processing` (retry), same for quiz `not_made->making->ready|failed`, `failed->making`. Every status has `status_changed_at`; a processing/making row older than N minutes is treated as failed when read (one `reap_stale()` called in the status view and at worker start). Jobs are enqueued with `transaction.on_commit`. Job input is only the primary key."

### F-9 (B) Rate-limit waiting inside the web request, and per-process limiter
- **Units:** U1 (essay feedback view, synchronous because EXPERIENCE says "Reading your answer..." in the same flow), U2 (summary job).
- **ADs:** AD-4 (`ai_client` owns "waiting and retrying on rate-limit errors"), AD-2.4 (jobs call the same services as views), seed diagram (Web --> AIC).
- **Divergence:** The wait is in `ai_client`, which the web app is explicitly allowed to call. On the Gemini free tier a 429 may mean a wait of tens of seconds; the Django dev server threads block, browser shows spinner, the PRD "pages respond in 2 seconds" and the `runserver` thread pool suffer. Web and worker are two processes, each with its own in-memory limiter, so two users plus a job exceed the shared key limit and the limiter never sees it. AD-4's retry budget (2 + waits) is unbounded in time.
- **Fix:** AD-3/AD-4: "No `ai_client` call is made from a web request. Every AI call is a queued job (essay feedback too), including its waiting. Rate-limit state (requests per minute and per day) lives in the database, one row, read and updated in a short transaction, so web and worker see the same budget. The wait is capped (e.g. 90 s), after which the job fails with a plain message."

### F-10 (B) django-q2 defaults contradict AD-3, AD-8 and AD-15
- **Units:** U1 (worker config in settings), U2 (summary job calling AI for a 50-page lecture).
- **ADs:** AD-3 (exactly one worker, safe twice, WAL), AD-4 (retries and waits), AD-8.6 (deleting removes everything), AD-15 (no lecture text in logs).
- **Divergence:** (a) `Q_CLUSTER timeout` default is 60 s, `retry` default is 120 s. A 50-page summary may take up to 120 s (FR-8) plus waits: the worker kills the task, then django-q2 re-queues it after `retry` and, if the first worker is still in the AI call, two copies run concurrently. "Check whether the result is stored" does not help: both see none and both pay the AI cost. (b) django-q2 persists every task's `args`, `kwargs` and `result` in `django_q_task` (and the broker row in `django_q_ormq`). If any session passes page text or the AI result as args/return value, lecture text and essays sit in a table that "delete lecture" never touches, and failures are stored with tracebacks that can contain input. (c) "exactly one worker" is `workers: 1`, but the cluster still has sentinel, pusher and monitor processes polling the broker table every fraction of a second, i.e. constant SQLite writes. (d) `retry` must exceed `timeout` and both must exceed the capped AI wait or you get re-queues.
- **Fix:** AD-3 add: "`Q_CLUSTER = {workers: 1, timeout: 240, retry: 300, max_attempts: 1, save_limit: -1, ack_failures: True, poll: 1}`. Jobs receive only integer ids and return None. `max_attempts: 1` because retry is our own explicit state transition. Idempotency is a database guard: the job's first action is the conditional `set_status` of F-8, which is the real lock; 'result already stored' is only a second check."

### F-11 (B) SQLite locking between web app, worker and open transactions
- **Units:** U1 (summary job writes parts atomically), U2 (quiz answer-check view), U3 (usage log).
- **ADs:** AD-3 ("WAL mode and a wait timeout"), AD-8.3 (one transaction), AD-4 (usage log).
- **Divergence:** "A wait timeout" has no value and no mode. Django wraps `atomic()` in a deferred `BEGIN`; a transaction that reads then writes while another writer commits gets `SQLITE_BUSY` immediately, ignoring the busy timeout (lock upgrade). A session that writes the whole result "in one transaction" naturally opens the transaction before the AI call (wrapping the use case), so the write lock is held for up to 120 s and every Check-answer save in the web app fails with "database is locked", which AD-11 turns into "failed save". The usage log (AD-4/AD-5.7) has no stated store; a session writes it with a DB insert on every call, another to the log file.
- **Fix (new AD):** "SQLite: `PRAGMA journal_mode=WAL; synchronous=NORMAL; foreign_keys=ON`, Django `OPTIONS: {timeout: 20, transaction_mode: 'IMMEDIATE'}` (Django 5.1+). No AI or PDF call inside `atomic()`. A transaction contains only the final write, and is under 1 second. AI usage log is rows in `AiCallLog` (counts/ids only)."

### F-12 (H) Deletion while a job runs
- **Units:** U1 (delete view), U2 (summary job or quiz job).
- **ADs:** AD-8.6 (deleting removes everything), AD-3, AD-8.3.
- **Divergence:** U1 deletes the Lecture (cascade) while the job holds the id. The job finishes the AI call (cost spent), then writes SummaryParts: `IntegrityError` (FKs on), or, with `get_or_create(lecture_id=...)`, orphans, or `set_status` raising `DoesNotExist` which the idempotent retry logic loops on. Also the Delete button is visible on a "Processing..." row (EXPERIENCE). Alternatively U1 refuses to delete while processing, and a stuck row (F-8) can never be deleted, which breaks FR-21 as a privacy safeguard.
- **Fix:** AD-8 add: "Delete is a conditional action: mark `deleted_at`/`status=deleting` via `set_status`, hide immediately, and remove after the job exits; jobs re-check the row exists and `status == processing` immediately before the final write and silently drop their output otherwise. Delete is allowed from any state, including stuck."

### F-13 (H) Immutable content vs retry/regenerate vs cascade
- **Units:** U1 (retry button for failed lecture), U2 ("Try again" on quiz), U3 (builder tool that re-runs after a Prompt change).
- **ADs:** AD-8.3 ("a retry replaces the whole result"), AD-3 ("stop if result already stored"), AD-8.6.
- **Divergence:** AD-8.3 says retries replace; AD-3 says a job stops if there is a result. A retry job started from a `failed` state with no rows is fine; a session that implements "regenerate" (for FR-30 or a user complaint) deletes SummaryParts, which cascades to Questions, Answers, Attempts, Reports (all FK to SummaryPart or Question) - a student's scores vanish silently. The other session's job sees stored result and stops, so regenerate never regenerates.
- **Fix:** AD-8.3 replace with: "A Summary is written once and never replaced after `ready`. Only a `failed` run (no rows exist) may be retried. A Quiz likewise. Regeneration of a ready lecture is not a v1 feature; evaluation uses its own in-memory path and writes nothing to user tables. FKs from Answer/Attempt/Report use `PROTECT` toward content so a stray delete fails loudly; only Lecture deletion cascades."

### F-14 (H) Daily upload limit races and day boundary
- **Units:** U1 (upload view), U2 (processing job "Try again"), U3 (settings).
- **ADs:** AD-15 (per user per calendar day from a database table; rejected uploads do not count), Conventions (dates in UTC).
- **Divergence:** "Calendar day" in UTC vs Europe/Oslo: a Norwegian student's 5 uploads reset at 01:00 or 02:00 local time, and the message "tomorrow" is wrong. Check-then-insert race: two simultaneous uploads both see 4. "Rejected uploads do not count" - but FR-4 rejection is only known after extraction, so the count row is inserted after extraction by one session and before by another. Does "Try again" for a failed lecture count? Does a lecture with failed processing refund? AD silent, so one session consumes a slot on each retry (FR-7 message appears while no upload happened) and another gives free AI calls on retries (F-15).
- **Fix:** AD-15: "Limit day is `settings.LIMIT_TIME_ZONE` (default Europe/Oslo) local date, stored in `UploadLog.local_day`. Insert-and-check happen in one IMMEDIATE transaction after validation succeeds and before enqueue. A retry does not create an UploadLog row but is capped at 3 retries per lecture."

### F-15 (H) Cost caps leak through retry, restart and quiz re-open
- **Units:** U1 (essay tab), U2 (quiz first open), U3 (lecture retry).
- **ADs:** AD-5 (calls per task), AD-3, FR-7 limit counts uploads only.
- **Divergence:** Every path is individually within the ADs yet unbounded together: "Start again" gives a fresh 3 essay submissions each time; quiz "Try again" has no cap; quiz first-open triggered by a GET can be fired repeatedly while `failed`; lecture retry unlimited. A single account can drain the shared free-tier key and block all other users (and the examiner's live demo with a key).
- **Fix:** New AD: "A per-user per-day AI call budget (setting) enforced in the same `AiCallLog` table, checked before enqueue; a hard global per-day ceiling too. Retry per object is capped (3)."

### F-16 (B) Demo Mode vs real mode when a key exists; Example Lecture state and `user = NULL`
- **Units:** U1 (`ai_client` mode), U2 (views and banner), U3 (example attempts).
- **ADs:** AD-10 (demo starts when no key; button always available; `is_example`; attempts in "browser session"), AD-4 (with no key never calls out), AD-8.2 (every query through the owner), AD-11 (same requests write to the browser session).
- **Divergence:**
  1. *Mode is global in one place, per-object in another.* `ai_client` decides demo by key presence; views decide by `lecture.is_example`; the banner by a session flag set by the button. With a key present, a visitor clicks "Try the demo", then Upload: the banner (session flag) says upload needs a key, while the key exists; or an `is_example` essay submission with free text reaches the real API and costs money; or with no key a registered user's real lecture essay hits replay and returns another lecture's canned feedback.
  2. *"Browser session".* AD-10.4 and AD-11 do not say Django session (server side, in `django_session` table, cookie 4 KB if signed-cookie engine) or `sessionStorage`. Two sessions build both; the results page and Review List (F-3) read DB `Attempt`/`Answer` in real mode and session dicts in demo mode, so every view needs two code paths that will drift.
  3. *`user = NULL`.* AD-8.2's "every query goes through the owner" becomes `filter(user=request.user) | filter(is_example=True)` in one session; any other mutation endpoint (answer save, draft, report, delete) that forgot to check `is_example` writes `Attempt(user=NULL)` rows that every anonymous visitor can then read - a cross-visitor leak that SM-7 does not test.
  4. The prepared essay answers have no table; "looked up from stored data" could be by answer text, id or index, and the replay used by tests (AD-14) is keyed differently.
- **Fix:** AD-10 add: "Mode is decided per object, never globally: `ai_client` never receives an example-lecture call at all (views route `is_example` essays to `demo_feedback(question_id, prepared_answer_id)`); real calls are made only if a key exists and the lecture is not an example. Banner shows when the *current lecture* is an example, plus on the login page when no key is set. Example-lecture progress is stored in the Django server-side session under one key `demo_progress`, with the same dataclasses as F-3; services expose `ProgressStore` with two implementations (DB, session) behind one interface so views have one code path. Models `Attempt/Answer/EssaySubmission` must have `user` NOT NULL (database constraint); only `Lecture`, `SummaryPart`, `Question`, `KeyTerm` may be example rows. All mutating endpoints go through `get_lecture_for_write(user, id)` which rejects example rows."

### F-17 (H) localStorage draft vs server draft vs submitted text
- **Units:** U1 (htmx autosave endpoint), U2 (JS backup script), U3 (submission view).
- **ADs:** AD-11 ("server copy wins unless the browser copy is newer"; backup cleared on logout; server draft saved after about 2 s).
- **Divergence:** "Newer" compares a browser clock with a server timestamp; with a 5-minute clock error, a stale browser draft overwrites a newer server text, or the reverse. After submission 1 the draft entity (F-1) is cleared by one session and kept by another, so the box shows the old submitted text, or, after submission 3, a newer browser copy tries to fill a read-only box. The localStorage key is not specified: `essay-<questionId>` is shared by every account on a campus computer; AD says cleared on logout, but a session timeout or closed tab never runs logout JS. Also htmx history snapshots are written to localStorage (see S-3).
- **Fix:** AD-11 replace "newer" with a monotonic `version` integer incremented by the server per save; the browser stores `{userId, attemptId, questionId, version, text}`; it wins only if `version >= serverVersion` and `savedAtClient` is after a server-issued nonce; the key includes the user id; cleared on page load when the logged-in user id differs, on submit and on logout. Server-side: the draft row belongs to (attempt, question) and is deleted in the same transaction that creates a submission; closed attempt boxes ignore drafts.

### F-18 (M) Attempt vs quiz status vs "resume"
- **Units:** U1 (quiz tab), U2 (results tab).
- **ADs:** AD-8.5 (quiz status), AD-11 (answer saved on check), EXPERIENCE ("Start again", resume, multiple tabs).
- **Divergence:** `Attempt` has no type and no finished state (ER). "Resume the unfinished quiz" is `latest attempt without finished_at` in one story, `attempt with fewer answers than questions` in another. Two browser tabs or devices create two open attempts. "Check answer" double click creates two Answer rows (no unique key), and the "answer cannot be changed after checking" rule is only a UI rule, so a second POST can overwrite correctness. Answer keys render into the HTML for the client (a template that dumps the question JSON) before checking.
- **Fix:** see F-1 schema; AD-8: "`Answer` is write-once (`UNIQUE(attempt, question)`, server refuses a second check). An attempt is open until `finished_at`; at most one open attempt per (user, quiz) enforced by a partial unique index; 'Start again' closes the old one. Templates receive question objects without the key until the answer exists."

---

## C. Security

### S-1 (H) Access control relies on discipline, nested ids are an IDOR gap
- **Units:** U1 (lecture views), U2 (htmx fragment endpoints: status, answer, draft, report, submission).
- **ADs:** AD-8.2, AD-7 ("access checks forgotten on single pages"), AD-2.1.
- **Divergence:** AD-8.2 says queries go through the owner but names no mechanism. U1 uses `get_object_or_404(Lecture, pk=pk, user=request.user)`. U2's `POST /answers/<attempt_id>/<question_id>/` fetches `Attempt.objects.get(pk=attempt_id)` because "it is only an htmx fragment" or checks the lecture and then loads the question by id from another lecture. The polling status endpoint returns different responses (401/403/404) for other users' ids; the redirect-to-login for logged out vs 404 for wrong user can leak existence (EXPERIENCE wants "no hint that it exists"). A user can then report, answer or read another user's question key.
- **Fix:** AD-8.2 add: "All reads and writes of user-owned rows go through one set of owner-scoped managers (`Lecture.objects.for_user(user)`), the only way views get a Lecture; children are reached only through the lecture (`lecture.questions.get(pk=)`), never by raw id. Wrong user, missing id and example-write all produce the same 404 body. Tests: for every URL in `urls.py` a generated test requests it as user B with user A's ids (SM-7)."

### S-2 (H) CSRF and htmx: stated but not specified; GET with side effects
- **Units:** U1 (htmx endpoints), U2 (quiz first-open, logout).
- **ADs:** Conventions "Django CSRF protection stays on for every form and htmx request".
- **Divergence:** Nothing says how the token reaches htmx requests. One session adds `{% csrf_token %}` in each form but htmx `hx-post` buttons and the autosave `hx-trigger="keyup delay:2s"` carry none: 403 on every save. htmx by default does not swap 4xx/5xx responses, so the 403 shows nothing, and AD-11's "failed save shows a plain message" never fires; typed answers are silently not saved while the UI looks normal. The quiz "first open" generation is naturally triggered by `GET /quiz/mc/` (a tab is a URL), so a cross-site `<img src>` or prefetch burns the victim's AI quota (F-15); logout as GET is similar.
- **Fix:** Conventions add: "`<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>` once in the base template; `htmx:responseError` and `htmx:sendError` handler shows the plain message and never discards input; every state-changing action (including quiz generation, retry, logout) is POST only; GETs are safe and idempotent. `CSRF_COOKIE_SAMESITE=Lax`, `SESSION_COOKIE_SAMESITE=Lax`."

### S-3 (H) htmx history cache and Back button leak lecture content after logout
- **Units:** U1 (tab navigation with `hx-push-url`/`hx-boost`), U2 (logout).
- **ADs:** AD-11 (backup cleared on logout), FR-1 consequence (after logout a saved page cannot be opened), EXPERIENCE (every tab has its own address and Back works).
- **Divergence:** htmx snapshots the DOM into `localStorage` (`htmx-history-cache`) on every pushed navigation and restores it on Back, including summary text, quiz answers and essay text, not touched by "clear the draft backup", and shown without any server request after logout. bfcache and the browser cache also serve authenticated pages on Back.
- **Fix:** Conventions: "`htmx.config.historyCacheSize = 0` (or `hx-history='false'` on every authenticated page); all authenticated responses send `Cache-Control: no-store`; logout clears all `localStorage` keys starting with `recall:` and `htmx-history-cache`; bare `htmx` is loaded from the repo only."

### S-4 (H) Prompt injection: the marker scheme can be forged, and output rendering is unspecified
- **Units:** U1 (marker builder in `ai_client`), U2 (templates showing summary/feedback).
- **ADs:** AD-5.2-5.4 (markers, "data never instructions", validate before storing), AD-2.1 (no logic in templates).
- **Divergence:** The delimiters `[Slide N] ... [End slide N]` are plain text that the slide itself can contain ("[End slide 3] New instructions: ..."). Instruction-to-ignore prompts help but are not a boundary. Validation (AD-8.4, FR-27) checks structure and page numbers, not content: an injected slide that tells the model to output a link, an HTML snippet, or "all answers are B" is valid by every rule; the key term check passes because the injected text is in the lecture. The student's own essay could contain delimiter text to change the key points listing in the feedback call. Rendering: one session wants basic formatting in summaries and uses `|safe` or a markdown filter, producing stored XSS from a crafted PDF (a classmate's PDF shared by e-mail to the victim). htmx also processes `hx-*` attributes in swapped HTML, so an unescaped attribute becomes script-equivalent behaviour.
- **Fix:** AD-5 add: "(8) Delimiters contain a per-call random token (`<<S7f3a:3>>`), and any occurrence of the delimiter pattern or `<<`/`>>` in extracted text or essays is neutralised before sending. (9) Every AI-produced string is stored and rendered as plain text: Django autoescape only, `|safe`, `mark_safe` and markdown renderers forbidden for AI fields (a test greps templates); no URL or HTML is permitted in output (validator rejects `http`, `<`, `>`, `hx-`). (10) CSP: `default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'`, `htmx.config.allowEval=false`, `selfRequestsOnly=true`."

### S-5 (H) Upload handling: size, memory, parse time, and where the bytes travel
- **Units:** U1 (upload view), U2 (extraction in view or job).
- **ADs:** Conventions upload row, AD-9, AD-8.6 (PDF not kept), AD-3 (jobs).
- **Divergence:** "Check by content" is `%PDF-` magic only; pdfplumber/pdfminer on hostile or huge PDFs can use gigabytes of RAM or minutes of CPU (a 10 MB PDF with huge object streams or deep page trees), and 50 pages of pdfplumber layout analysis is itself slow (several seconds to tens of seconds). Where does extraction run? FR-3/4 want immediate rejection, creating no Lecture, which argues for the web request; AD-3 and the 2 s page-time rule argue for the worker. U1 extracts in the view, hangs one dev-server thread; U2 uploads, creates a Lecture, extracts in the job, and a scanned PDF becomes a "Failed" lecture instead of an inline rejection. The 10 MB limit is checked via `Content-Length` or `file.size` after Django has already received and spooled the whole body (the dev server has no body limit), so a 4 GB upload fills disk. A session adds `FileField(upload_to=...)` on `Lecture`, keeping the original PDF, contradicting AD-8.6. Passing PDF bytes or extracted text through django-q2 args stores them in `django_q_ormq` / `django_q_task` (F-10). Encrypted PDFs raise a pdfminer error that surfaces as a 500. Pdf bomb timeout nothing.
- **Fix:** AD-9/AD-15: "Upload pipeline is: stream with a hard cap (`DATA_UPLOAD_MAX_MEMORY_SIZE`, `FILE_UPLOAD_HANDLERS` set to `TemporaryFileUploadHandler`, view aborts at 10 MB+1 by counting bytes); check `%PDF-` header; run `extract_pages` in a subprocess with a 20 s timeout and a memory cap (or in the worker as a first job whose failure is shown inline by the polling page, with no Lecture row visible in the list for rejected-type failures); on success write `PageText` rows; delete the temp file in `finally`. Job args are ids only. Encrypted/corrupt PDF maps to the 'no readable text' message. No `FileField` on any model."

### S-6 (M) Logs can still contain content
- **Units:** U1 (error handling in `ai_client`), U2 (django-q2 failure handler).
- **ADs:** AD-15 ("never lecture text, essay answers, passwords or keys"), AD-5.7.
- **Divergence:** The rule bans writing content deliberately. `logger.exception()` of a pydantic `ValidationError` (used by the Gemini SDK and by structured-output parsing) prints `input_value=...` with the offending model output, which contains lecture text; google-genai exceptions carry the request in some failure modes; django-q2 logs failed task args; Django logs POST data in 400 debug pages. Also `RotatingFileHandler` with two processes (web and worker both started by `run.py`) writing the same `logs/recall.log` fails on Windows at rotation (`PermissionError: file in use`) and can lose the worker's logging silently.
- **Fix:** AD-15 add: "Exceptions are logged by class name and a code only (`log_safe_exc(e)`), never `exc_info` from AI, parsing or validation code; `hide_input_in_errors=True`. One log file per process (`web.log`, `worker.log`)."

### S-7 (M) Accounts: case-insensitive e-mail, brute force, redirect
- **Units:** U1 (register), U2 (login).
- **ADs:** AD-7 ("username is the email address").
- **Divergence:** U1 lowercases on register (`normalize_email` only lowercases the domain part); U2 authenticates exact-case. "Amara@x.no" and "amara@x.no" become two accounts that each see different lectures, or login fails for the second spelling. No throttling on login (a free-tier AI key is not the only valuable asset: essays). `next` redirect unvalidated.
- **Fix:** AD-7 add: "e-mail stored lower-cased and stripped; unique index on `lower(email)`; login throttle (5 failures / 15 min / account+IP using the cache, DB-backed); `next` validated with `url_has_allowed_host_and_scheme`; default Django password validators on."

---

## D. Fresh clone, no keys, README only (SM-9, FR-24)

### D-1 (B) A placeholder key turns off Demo Mode
- **Units:** U1 (`.env.example`), U2 (README step "copy `.env.example` to `.env`").
- **ADs:** AD-12 (`.env.example` lists every setting with a comment), AD-4/AD-10 (demo starts when "no API key is set").
- **Divergence:** U1 writes `GEMINI_API_KEY=your-key-here` (a documented setting with a comment, as AD-12 demands). The README tells the examiner to copy it to `.env`. django-environ returns the non-empty string; `ai_client` sees "a key", calls Google, gets 400 on every call, and the examiner sees "Failed" on a lecture and no demo banner. In the other direction, google-genai's own client reads `GEMINI_API_KEY` / `GOOGLE_API_KEY` from the process environment: an examiner who has one set globally gets real calls even though `.env` says nothing.
- **Fix:** AD-12/AD-10: "A key is present only if it is non-empty after stripping, is not in a known placeholder list, and matches a plausible shape; `.env.example` ships `GEMINI_API_KEY=` (empty). `ai_client` always passes the key explicitly and never constructs a client in demo mode. A test starts the app with a hostile environment variable and with a copied `.env.example`."

### D-2 (B) Cannot start with no `.env`: DEBUG default and static files
- **Units:** U1 (`settings.py`), U2 (`run.py`).
- **ADs:** AD-12 (starts with no `.env`; SECRET_KEY falls back when DEBUG is on and stops when off), AD-15 (`run.py` starts web and worker).
- **Divergence:** AD-12 does not state the default for `DEBUG`. U1 follows security habits and defaults `DEBUG=False`: a fresh clone stops with the SECRET_KEY message, failing FR-24 outright. U1' defaults `DEBUG=True`, which makes AD-15's deploy checklist a trap. With DEBUG off, `runserver` does not serve static files, so the htmx script, CSS and text-size control 404 and the UI is dead; and `ALLOWED_HOSTS` is empty then. Also `run.py` using `runserver` with the autoreloader starts two copies of its child, and the reloader may start duplicates of the worker.
- **Fix:** AD-12 add: "`DEBUG` default is True only when `RECALL_ENV` is unset or `local`; `run.py` sets `RECALL_ENV=local` and calls `runserver --noreload` with `--insecure`-free static serving through WhiteNoise (added to the stack list) so the same path works with DEBUG off. `ALLOWED_HOSTS` default `localhost,127.0.0.1`. `run.py` is a tested entry point: it runs `migrate`, loads the example lecture, then starts both processes, and kills both on Ctrl+C on Windows via `CTRL_BREAK_EVENT`/process group."

### D-3 (B) Example Lecture loading: who, when, how many times
- **Units:** U1 (migration), U2 (`run.py` or `AppConfig.ready()`).
- **ADs:** AD-10.5 ("setup loads the example data on first run, with no manual step"), AD-14 (tests).
- **Divergence:** One session loads in a `RunPython` data migration; tests then contain an extra Lecture in every test database (counts in SM-7/SM-8 tests break), and the JSON schema is frozen at migration time. The other loads at startup in `ready()`: web and worker start simultaneously, both see no example, both insert, producing two Example Lectures with two sets of ids. Nothing enforces a unique example.
- **Fix:** AD-10: "Loaded by `manage.py load_example` only, called by `run.py` before starting the processes and by the README as one command; idempotent via a stable key (`Lecture.example_key` unique, `get_or_create`), run in one IMMEDIATE transaction. Tests create their own example from a small fixture."

### D-4 (H) Frozen files and prompt fingerprints break on Windows checkouts
- **Units:** U1 (test set fingerprint), U2 (prompt fingerprint).
- **ADs:** AD-13.4 (fingerprint of `evaluation/testset/`; test fails if files change), AD-6 (fingerprint of prompt file text).
- **Divergence:** Git for Windows defaults `core.autocrlf=true`. The builder generates fingerprints on one checkout, the examiner's fresh clone converts line endings: the hash differs and `python manage.py test` fails on a clean clone - the examiner's first impression. The `.env`-tracked-by-git test (AD-12) also needs the `git` binary and a `.git` folder, absent when the repo arrives as a ZIP.
- **Fix:** AD-6/AD-13: "fingerprints are computed on bytes after normalising `\r\n` to `\n`; `.gitattributes` marks `*.md`, `*.json`, `*.txt` as `text eol=lf`. The 'no secrets in git' test skips with a message when git is unavailable, and has a file-system scan fallback."

### D-5 (M) Versions and Python on the examiner's machine
- **Units:** U1 (`requirements.txt`), U2 (README).
- **ADs:** AD-12 (exact versions), Stack ("Python 3.12 or newer").
- **Divergence:** "or newer" with exact pins: pdfplumber → pypdfium2/Pillow/cryptography wheels and django-q2 dependencies may have no wheel for a very recent Python, forcing a compile step on Windows that the README does not mention. The deferred django-q2 job test is "at install" on the builder's machine only.
- **Fix:** Stack: "Python 3.12 or 3.13 only (tested); `run.py` and README check `sys.version_info` and print a plain message; CI-style script `scripts/fresh_clone_check.ps1` runs: new venv, `pip install -r requirements.txt`, `run.py`, GET `/`, GET demo, POST an example answer, upload with no key. Record it in `docs/`."

---

## E. Consistency gaps worth closing in the conventions table

- **Naming collision:** the UI says "attempt" for an Essay Submission; the model `Attempt` is a quiz run. Add: "In code, 'attempt' always means `Attempt`; student-visible 'Attempt 2 of 3' comes from `EssaySubmission.seq`. A glossary comment in `models.py`."
- **Report vs deletion (FR-22/FR-31):** `Report -> Question` cascade through Lecture deletion destroys the evidence the builder needs. Fix: Report copies question text, key, Source Reference, prompt version and model into its own columns, FK `SET_NULL`.
- **Which prompt/model produced this content:** AD-5.7 logs it but nothing stores it on Lecture/Quiz, so a report cannot be traced to a prompt version. Add `generated_with` (model, prompt version) to Lecture and Quiz.
- **Status polling endpoint scope:** AD-11 says "a status view"; Lecture and the three Quiz statuses and EssaySubmission status each get one. Specify one URL shape `/status/<kind>/<id>/` and one partial template.
- **Test replay keys:** AD-14 replay of "stored sample responses" and AD-10 demo replay both use `ai_client` replay; specify one key (task + fixture name), or tests will call the demo path.

---

## Top findings (ranked)

1. F-16 Demo vs real mode: global vs per-object, session vs DB state, `user = NULL` leak (B)
2. F-10 + F-8 django-q2 defaults (60 s timeout, re-queue, persisted args) and the hollow `set_status()` (B)
3. F-1 Missing entities (page text, quiz, draft, upload log) invented twice (B)
4. D-1/D-2/D-3/D-4 Fresh-clone failures: placeholder key, DEBUG default and static files, double-loaded example, CRLF fingerprints (B)
5. F-9 + F-11 Rate-limit wait in a request, per-process limiter, SQLite lock held across AI calls (B)
6. S-3 + S-2 + S-4 htmx localStorage history leak, CSRF headers/silent 403, forgeable prompt delimiters and unspecified rendering (H)
7. F-5 + F-6 Two validators/normalisers: grounding outside the retry loop, ligature failures (H)

## Must-fix additions before stories are written

| New / tightened AD | Closes |
| --- | --- |
| AD-17 Complete entity list with constraints (F-1, F-4, F-18) | table gaps, write-once answers, submission seq |
| AD-3 tightened: `set_status` conditional, edges listed, stale reaper, `on_commit`, ids-only jobs, `Q_CLUSTER` values (F-8, F-10, F-12) | duplicate runs, stuck processing, persisted text |
| AD-3/AD-4: AI only in jobs, DB-backed shared limiter, wait cap, shared retry budget, validator inside the retry loop (F-5, F-9, F-15) | request-blocking, cost leaks |
| SQLite AD: pragmas, `IMMEDIATE`, no AI inside `atomic()` (F-11) | `database is locked` |
| AD-10 tightened: per-object demo routing, `ProgressStore` interface, `user` NOT NULL on attempt tables, `load_example` command (F-16, D-3) | demo drift and leak |
| AD-8.2 tightened: owner-scoped managers, uniform 404, generated URL x user test (S-1) | IDOR |
| Conventions: SourceRef type, `core/types.py` dataclasses, `normalize_text()` (F-2, F-3, F-6, F-7) | shape divergence |
| Security conventions: CSRF header and error handler, POST-only mutations, history cache off, no-store, CSP, plain-text rendering, random delimiters, upload pipeline (S-2..S-5) | web security |
| AD-12 tightened: key-present rule, DEBUG/`RECALL_ENV` default, WhiteNoise, `run.py` steps, `.gitattributes`, supported Python versions, fresh-clone script (D-1..D-5) | SM-9 / FR-24 |
