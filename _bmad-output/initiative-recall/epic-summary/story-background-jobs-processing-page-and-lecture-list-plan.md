---
title: 'Background jobs, Processing page and lecture list'
type: 'feature'
ticket: '2'
created: '2026-11-25'
status: 'built'
baseline_revision: '40725f98d103f9a22e5a226967e8cde49ff9d58a'
route: 'full'
route_source: 'auto'
risk: 'high'
review: 'quick'
review_source: 'pinned'
lenses_ran: [quick]
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-recall/architecture-recall/architecture-recall.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** An uploaded lecture sits in `processing` forever: nothing runs it, nothing shows its status, and a stuck or failed one cannot be retried.

**Approach:** One worker (django-q2, one process) runs jobs behind `jobs.enqueue(name, object_id)`. Every status change goes through `set_status()`. A Processing page and My lectures list show the real status by polling. The job body is a stub that ends the lecture as Failed; story 3.3 replaces it. No AI call, no Gemini key.

## Boundaries & Constraints

**Always:** The PDF is never stored. Every new table is owner-scoped (`for_user`) or pure infrastructure with no content (django-q2 tables). Every new address goes through `get_lecture` / `get_lecture_for_write`: wrong owner and missing id give the same bare 404, and the owner check runs before the method check. Jobs get an integer id and return nothing; `enqueue` runs in `transaction.on_commit`. Only `core/jobs.py` imports django_q. Services never import jobs; views and jobs call services. Logs carry no content. README describes only what the app does now. Python commands use `.venv/Scripts/python`.

**Never:** No AI call, no Gemini import, no key needed. Do not change upload validation, the daily limit or owner-scoped rules. No Summary. No percentage, timer or invented steps. No commit. django-q2 is installed only after the user's yes, only into `.venv`. Any test server or worker is stopped when done.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Page closed | `processing` lecture, tab closed | Worker finishes; list later shows Failed (stub) | none |
| Double enqueue | same id twice | First `set_status` True, second False; second does nothing | none |
| Stale | `processing` older than 10 min | Treated as `failed`, retry shown | `reap_stale()` at `run.py` start and in status view |
| Retry 1-3 | failed lecture, POST | back to `processing`, `retry_count`+1, job queued | none |
| Retry 4 | `retry_count` = 3 | refused, plain message, no change | no job queued |
| Budget used | per-user or global AI budget spent | nothing queued, clear message | no status change |
| Other user | user B asks status/retry of A's id | same bare 404 | none |

**Decisions (user, 2026-11-25):** Add a minimal `AiCallLog` here (AD-17 columns: user, task, model, prompt version, token counts, wait time, timestamp), owner-scoped with `for_user` like the other tables, with a migration. Nothing writes to it in this story; **story 3.1 must write one row per AI call**, and the budget check reads it. Keep the full plan, no split. django-q2 and its dependencies are pinned in `requirements.txt` with exact versions after install, once the user has seen the PyPI metadata and said yes.

</frozen-after-approval>

## Code Map

- `lectures/models.py` -- `Lecture` already has `status`, `status_changed_at`, `retry_count`; add status constants; `for_user` is the door. No migration needed for these.
- `lectures/services.py` -- add `set_status`, `reap_stale`, `retry_lecture`, budget check; `create_lecture_from_upload` stays as is (it creates `processing` rows).
- `lectures/views.py`, `lectures/urls.py` -- `lecture_detail` stub becomes the Processing page; add retry view.
- `config/views.py`, `config/urls.py` -- `lectures` list view; new `status/lecture/<int:lecture_id>/` route.
- `core/jobs.py` (new) -- the only django_q import; `core/tests.py` already allows it there.
- `run.py` -- today starts `runserver` only; `bind_children_to_this_process()` (Windows job object, kill on close), `stop_server`, polling loop, SIGBREAK handler already fix the story 1.1 bug. Reuse them for the worker.
- `config/tests.py` -- `RunPyStopsServerTests`, `_SERVE_WRAPPER` pattern to extend; `ReadmeTests` + `docs/required_readme_headings.txt`.
- `config/test_url_access.py` -- walks `urls.py`; new routes are covered automatically.
- `config/settings.py`, `.env.example`, `requirements.txt`, `README.md`, `templates/` (`lectures.html`, `lectures/detail.html`, new partial `lectures/_status.html`, `base.html` has htmx and CSP `script-src 'self'`).

## Tasks & Acceptance

**Execution:**
- [ ] `requirements.txt`, `config/settings.py`, `.env.example` -- add django-q2 (after approval), `django_q` app, `Q_CLUSTER` (workers 1, timeout 240, retry 300, max_attempts 1, no stored successes; check names against the installed docs), `STALE_MINUTES=10`, `POLL_SECONDS=3`, `RETRY_LIMIT=3`, `AI_CALLS_PER_USER_PER_DAY`, `AI_CALLS_GLOBAL_PER_DAY`, optional `DATABASE_FILE` -- named settings (AD-12.5)
- [ ] `lectures/services.py` -- `set_status(lecture, from_states, to_state)` as one conditional UPDATE, returns bool, allowed edges only; `reap_stale()`; `retry_lecture(user, id)` limited to 3; budget check -- AD-3, AD-23
- [ ] `core/jobs.py` -- `enqueue(name, object_id)` (int id, `on_commit`), stub job whose first action is `set_status(processing→failed)`; thread fallback only if django-q2 fails on Windows -- AD-3
- [ ] `lectures/views.py`, `config/views.py`, `*/urls.py`, templates -- Processing page, status partial (htmx every 3 s, no trigger once Ready/Failed, `aria-live`), My lectures with Processing…/Ready/Failed, retry button -- AC 6, 7
- [ ] `run.py` -- run `reap_stale` after migrate, start `manage.py qcluster` and `runserver` together, stop both on Ctrl+C, and stop the other if one exits -- AC 8
- [ ] `lectures/tests.py`, `config/tests.py` -- the tests named in the story, plus real worker run and Ctrl+Break stops both
- [ ] `docs/django-q2-windows-test.md`, `README.md`, `docs/required_readme_headings.txt` -- record the Windows result; add "How processing works" and "If you deploy this"; update Install step 4 -- AC 8, 10

**Acceptance Criteria:**
- Given the story's ACs 1-10, when `.venv/Scripts/python manage.py test` runs with no `.env`, then all pass and no test needs a key or network.

## Implementation Notes

Built directly, no subagent (none was requested). Files: `core/jobs.py`, `lectures/{models,services,views,urls}.py`, `lectures/migrations/0004_aicalllog.py`, `lectures/management/commands/reap_stale.py`, `lectures/test_processing.py`, `config/{settings,views,urls,tests}.py`, `run.py`, templates `lectures.html`, `lectures/{detail,_status,_status_row}.html`, README, `docs/django-q2-windows-test.md`, `.env.example`, `requirements.txt` (django-q2 1.11.1, django-picklefield 3.4.0).
- django-q2 runs on Windows: the thread fallback was not built.
- The budget check was added to the upload service beside the daily-limit check (AD-20 step 5). Defaults 30 per user and 200 global are my choice; both are env settings.
- `AiCallLog` has `local_day`; story 3.1 must set it when it writes a row.
- `DATABASE_FILE` setting added so tests run a worker on a throwaway database.
- Not done: `logs/worker.log` (AD-15.2); the worker logs to the console only.
- Review: the independent review lens was not run (no subagent permission). I read the diff myself and found no unmet AC. Full suite: 105 tests OK.

## Plan Change Log

- 2026-11-25 (review of story 3.2, finding 9, not a loop-back): while building, `run.py`'s `stop_server` was renamed `stop_process`, and `stop_all(children)` was added, because it now stops two children. The Code Map and Design Notes still say `stop_server`. The frozen block is untouched and the name is not part of any acceptance criterion; the code is the source of truth. No code was reverted.

## Review Triage Log

Pass 1, 2026-11-25. Quick lens (reviewer subagent, all six focus questions). 11 findings: 1 medium, 6 low, 3 false, 1 not triaged by verdict (plan wording). No intent_gap or bad_plan, so no loop-back.

| # | Finding | Verdict | Route | Evidence / action |
|---|---------|---------|-------|-------------------|
| 1 | `serve()` had no `finally`; a failed start of the worker or a second Ctrl+C could leave the web app running | low | patch (done) | `finally: stop_all(children)` added in `run.py`; test `RunPyCleanUpTests` makes the worker start fail and checks the server is stopped |
| 2 | macOS/Linux: SIGTERM to `run.py` leaves both children running | low | defer | Pre-existing since story 1.1; README known limit added; entry in `deferred-work.md` |
| 3 | A job queued longer than 10 min is reaped; a retry then queues a second job; a killed worker's task is redelivered after 300 s. The stub is safe, a real job is not | low now, medium for 3.3 | defer | Entry in `deferred-work.md`: story 3.3 must add a claim step or generation counter before the real Summary job |
| 4 | django-q2 stores failed tasks as `"{error} : {traceback}"` and never prunes them, so an exception with slide text would persist (the earlier test comment claimed more than it checked) | medium (latent) | patch (done) | `core/jobs.py` `run_job` logs only the class name and raises `JobFailed(<class name>) from None`; new test fails if the original error is chained (checked by temporarily chaining it) and checks the stored string and the log have no slide text; test comment corrected |
| 5 | Enqueue failing after commit leaves a lecture in `processing` with no job | low | rejected | The 10-minute reaper marks it failed and Try again appears |
| 6 | `reap_stale()` runs before the 404 | false | rejected | The response is identical for wrong owner and missing id; AC 4 requires reaping in the status view |
| 7 | AI budget counts only logged calls, is not atomic, user-delete cascade | false / low | rejected | Counting logged calls is the decision (AD-23, your choice A); queued work is bounded by 5 uploads a day plus 3 retries each; the docstring is about deleting a lecture |
| 8 | `_pid_alive` used a substring match | low | patch (done) | Now parses `tasklist /FO CSV` and compares the PID column |
| 9 | Plan text says `stop_server`, code says `stop_process` | n/a | rejected as an edit | Noted in the Plan Change Log |
| 10 | A refused Try again from the list shows the lecture page (400) | low | defer | UX gap for the polish epic, entry in `deferred-work.md` |
| 11 | `set_status` does not update `status_changed_at` on the in-memory object | false | rejected | Nothing reads it; the next read is from the database |
| 12 | Found by the user's manual test (real terminal Ctrl+C): django-q2 logs CRITICAL "reincarnated worker/monitor/pusher after sudden death" before the clean stop, because Ctrl+C also reaches the worker's child processes and the guard restarts them. Nothing is left running | low (looks alarming, result correct) | defer | A fix was proposed (children ignore SIGINT) and a test was started, but the real-Ctrl+C test could not be made to reproduce it in time, so the code was left as it is by the user's decision. README known limit and `deferred-work.md` entry added |

## Design Notes

- `run.py` starts two children: `manage.py runserver --noreload` and `manage.py qcluster`. Both stay under the Windows job object already bound to `run.py` (killed if `run.py` dies). The wait loop polls both; Ctrl+C or Ctrl+Break calls `stop_server` on each (3 s grace, then `taskkill /F /T`, which also ends the cluster's child processes). Tests prove it on Windows by checking that both the port and the worker process are gone.
- Stub job: one run moves `processing→failed`, so a second enqueue gets `False`. Story 3.3 must keep `set_status` as the lock.
- Budget check is one added step beside the daily-limit check; no existing check changes.

## Verification

**Commands:**
- `.venv/Scripts/python manage.py test` -- expected: all pass
- `.venv/Scripts/python manage.py makemigrations --check` -- expected: no changes (or only the planned ones)

**Manual checks (if no CLI):**
- `.venv/Scripts/python run.py`, upload, close the tab, reopen My lectures: shows Failed with a retry button; Ctrl+C leaves no `python` process of the app.

