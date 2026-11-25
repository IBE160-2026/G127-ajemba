
- source_plan: `_bmad-output/initiative-recall/epic-upload-pdf-checks/story-upload-a-pdf-with-all-checks-plan.md`
  summary: Add the AD-20 memory cap to the PDF extraction subprocess.
  evidence: Only the 20 s limit is enforced; Windows has no portable per-process memory cap in the standard library (a Job Object or `resource` on Linux would be needed). A hostile PDF within 10 MB can use much memory for up to 20 s.

- source_plan: `_bmad-output/initiative-recall/epic-upload-pdf-checks/story-upload-notice-acknowledgement-and-daily-limit-plan.md`
  summary: Changing `LIMIT_TIME_ZONE` on a running app can let one extra upload through, or block one, around the change.
  evidence: `UploadLog.local_day` is stored in the zone active at upload time and is compared with "today" in the new zone, so the same real day can be counted twice or not at all. Operator-only edge case found by the story 2.3 review; a fix (store UTC bounds, or recompute `local_day`) adds complexity. Limit raised or lowered through `UPLOADS_PER_DAY` works correctly.

- source_plan: `_bmad-output/initiative-recall/epic-summary/story-background-jobs-processing-page-and-lecture-list-plan.md`
  summary: Story 3.3 must add a claim step or a generation counter before the real Summary job replaces the stub.
  evidence: Story 3.2 only has `set_status` on the last change. A lecture that waits more than 10 minutes in the queue is reaped as failed, the user retries, and the old queued job then runs on the retried lecture (a second job for one lecture). A worker killed mid-job also gets its task again after `retry` (300 s). The stub is safe, because its only action is `processing -> failed`. A real job that does AI work before its final write is not. Add a claim step (for example a `claimed_by` token or an `attempt` counter on `Lecture`, set together with the status change and checked before the final write), found by the story 3.2 review.

- source_plan: `_bmad-output/initiative-recall/epic-summary/story-background-jobs-processing-page-and-lecture-list-plan.md`
  summary: On macOS and Linux, killing `run.py` with SIGTERM or SIGHUP leaves the web app and the worker running.
  evidence: Only Windows has the job object that kills the children when `run.py` ends, and only SIGBREAK has a handler. This was already true for the web app in story 1.1; the worker adds a second child. The README names Ctrl+C as the supported way to stop it on macOS and Linux. Fix if those systems are ever supported: handle SIGTERM and SIGHUP like Ctrl+C.

- source_plan: `_bmad-output/initiative-recall/epic-summary/story-background-jobs-processing-page-and-lecture-list-plan.md`
  summary: UX gap for the polish epic: a refused "Try again" from My lectures shows the lecture's own page (status 400) instead of the list.
  evidence: The retry button on the list is a plain form post, so a refusal (retry limit, AI budget) replaces the list with the lecture page that shows the message. It works, but the user loses their place. Fix: send the refusal back to the list with the message on the lecture's card, or post the retry with htmx and swap only that card. Found by the story 3.2 review.

- source_plan: `_bmad-output/initiative-recall/epic-summary/story-background-jobs-processing-page-and-lecture-list-plan.md`
  summary: A real Ctrl+C makes django-q2 log CRITICAL "reincarnated worker/monitor/pusher after sudden death" lines before the clean stop.
  evidence: Found by the user's manual test of story 3.2 (real terminal; nothing was left running afterwards). The terminal sends Ctrl+C to every process on the console. django-q2 makes only its sentinel ignore it (`cluster.py` line 175), so the pusher, monitor and worker processes die and the sentinel's guard restarts them. A separate process group alone would not fix it: the only clean stop in django-q2 is its in-process SIGINT/SIGTERM handler, and CTRL_BREAK would kill the whole group at once. Proposed fix, not built: a function in `core/jobs.py` called from `LecturesConfig.ready()` that sets SIGINT to ignore when `multiprocessing.parent_process()` is not None, so the cluster's main process still stops cleanly. It needs a test that sends a real CTRL_C_EVENT to a hidden console (attach with AttachConsole, then GenerateConsoleCtrlEvent). A first try failed to reproduce: `run.py` did not exit after the event in that test, and a probe run on a database without the cache table only showed `no such table: recall_cache` errors, so the setup needs to be fixed first (run `createcachetable` in the test database).


- source_plan: `_bmad-output/initiative-recall/epic-summary/story-gemini-key-model-choice-and-ai-client-with-replay-mode-plan.md`
  summary: Story 3.3 must pass one shared `JobBudget` to every `ai_client.call` in a job, or AI_JOB_BUDGET_S is not enforced.
  evidence: `call()` makes a new 220 s budget when none is passed; no caller exists yet, so 3.3 is where the bound is won or lost.
- source_plan: `_bmad-output/initiative-recall/epic-summary/story-gemini-key-model-choice-and-ai-client-with-replay-mode-plan.md`
  summary: Add deliberately broken stored replay samples (bad JSON shape, wrong slide numbers) with the validators.
  evidence: AD-14 asks for broken samples; only one valid sample exists and validators are story 3.3.

- source_plan: `_bmad-output/initiative-recall/epic-summary/story-summary-generation-with-validation-and-retries-plan.md`
  summary: A lecture refused for too much text (MAX_PROMPT_CHARS) shows only the generic Failed text, and Try again cannot help.
  evidence: `Lecture` has no field for a failure message; `run_summary` logs `reason=too_long` only. Fix: store a short reason code on the lecture and show the "too much text" message on the Processing page and the list, and hide Try again for it. Found by the story 3.3 review. The 50-page limit makes it rare.
