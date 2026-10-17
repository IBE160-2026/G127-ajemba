# Review: technology claims in architecture-recall.md (web-verified 2026-10-17)

Verdict: the stack choices hold up. Nothing is wrong enough to block, but several items are stale, unconfirmed, or missing a concrete number. Fix the Stack table and AD-3/AD-4 wording. Web access was via fetch/search; where a page was truncated or silent, the item is marked UNCONFIRMED.

## Verified versions (as of 2026-10-17)

| Item | Finding | Source |
| --- | --- | --- |
| Django | 5.2 LTS, latest patch 5.2.18. Mainstream support ended 2025-12-03; extended (security) support to April 2028. Newest series 6.1.2; 6.2 LTS not yet released. | https://www.djangoproject.com/download/ |
| Django 5.2 Python | 3.10, 3.11, 3.12, 3.13, 3.14 (3.14 from 5.2.8). | https://docs.djangoproject.com/en/5.2/faq/install/ |
| django-q2 | 1.11.1 (2026-08-26). requires Python >=3.10,<4; requires django>=5.2; tested with Django 5.2, 6.0, 6.1. | https://pypi.org/pypi/django-q2/json |
| pdfplumber | 0.11.10 (2026-06-15). MIT (classifier; `license` field is null). requires Python >=3.8. Deps: pdfminer.six==20260107, Pillow>=12.2.0, pypdfium2>=5.9.0. | https://pypi.org/pypi/pdfplumber/json |
| google-genai | 2.31.0 (GitHub release 2026-10-14). requires Python >=3.10. | https://pypi.org/pypi/google-genai/json , https://github.com/googleapis/python-genai/releases |
| django-environ | 0.14.0 (2026-06-18). Python >=3.9. Classifiers list Django 5.2 and 6.0. | https://pypi.org/pypi/django-environ/json |
| htmx | Latest 2.x seen: v2.0.10 (6 Sep, year not shown on page). v4.0.0 is marked "Latest" on GitHub (28 Aug). | https://github.com/bigskysoftware/htmx/releases |
| Python | 3.10 EOL 2026-10-01. 3.11 to 2027-10; 3.12 to 2028-10; 3.13 to 2029-10; 3.14 bugfix to 2030-10; 3.15 scheduled release 2026-10-09. | https://devguide.python.org/versions/ |

## Findings

### F1 (medium) Python "3.12 or newer" is loose; pick one
Django 5.2 supports 3.10 to 3.14, and every pinned library supports 3.12+. Recommendation: Python 3.13 (security support to 2029-10, wheels mature) or 3.12 (to 2028-10). Avoid 3.15 (just released, third-party wheels such as Pillow/pypdfium2 may lag). Avoid 3.14 only if a wheel is missing at install. "3.12 or newer" invites students on 3.15 with missing wheels. State "3.13, tested; 3.12 acceptable".

### F2 (medium) Django row: "5.2 LTS" is correct but add dates and a 6.x note
5.2.18 is the current patch. Extended support to April 2028 is fine for a course project. The spine does not mention that 5.2 is no longer in mainstream support (only security fixes). Harmless, but say "pin 5.2.x, do not move to 6.x during the project".

### F3 (medium) django-q2: version, SQLite and Windows
- Version: 1.11.1 supports Django 5.2; the spine's "latest stable that supports 5.2" is satisfied. Pin 1.11.1 (or whatever the install test passes).
- SQLite "database is locked": one historical issue exists (django-q2 #144, closed 2023-12-05, https://github.com/django-q2/django-q2/issues?q=sqlite+locked). The docs configure page says nothing about SQLite; it only advises a separate database for better ORM-broker performance (https://raw.githubusercontent.com/django-q2/django-q2/master/docs/configure.rst). The spine's mitigation (WAL, busy timeout, one worker) is reasonable but is from general SQLite knowledge, not django-q2 docs. UNCONFIRMED as sufficient: keep the install-time job test, and add a concurrent poll-plus-job test.
- Windows: the install docs say "Forking isn't supported on Windows, so the cluster and worker multiprocessing code won't run there. For development, set sync to True" and the monitor/info commands need curses (https://github.com/django-q2/django-q2/blob/master/docs/install.rst). That page also lists only Python 3.8 to 3.12 and Django up to 5.0, so it is stale in places, but the Windows warning has not been contradicted. AD-15 asserts "run.py ... works on Windows" and AD-3 relies on a real background worker; this is the single biggest unverified claim. Windows uses spawn, so a cluster may work, but this must be tested early, not at install of AD-3's pin. Fallback to name in the spine: a small custom management command worker thread, or `sync=True` with a thread, if the cluster fails on Windows. Do not use `manage.py qmonitor`/`qinfo` on Windows.
- Q_CLUSTER for one worker (from the configure docs): `workers: 1`, `orm: 'default'`, `timeout` (default no limit; set it above the longest AI call), `retry` (default 60 s; MUST be larger than `timeout`, otherwise a slow task is re-queued and runs twice, doubling AI cost, which is exactly what AD-3 wants to prevent), `max_attempts` (default 0 = infinite retries; set to 1 to 3 so a failing job cannot loop and burn quota), `ack_failures` (default False; consider True), `poll` (default 0.2 s, fine), `bulk: 1`, `sync` (testing). Add these to AD-3; the spine currently says only "exactly one worker".

### F4 (high) Gemini model: the spine's Deferred row is right, but the facts it defers now matter
- Free-tier models per Google pricing page now include Gemini 3.8 Flash, 3.6 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, 3 Flash Preview, 2.5 Pro, 2.5 Flash, 2.5 Flash-Lite, Gemma 4, among others (https://ai.google.dev/gemini-api/docs/pricing).
- Deprecations page (last updated 2026-10-12): gemini-2.0-flash and 2.0-flash-lite shut down 2026-06-01 (already gone). gemini-2.5-flash / 2.5-flash-lite / 2.5-pro: no shutdown date, but "served until further notice ... limited to users who have used them before"; for new projects Google recommends 3.5 Flash-Lite or 3.8 Flash. gemini-3.1-flash-lite shuts down 2027-05-07 (replacement 3.5 Flash-Lite). Preview models (`gemini-3-flash-preview`, `-preview` names) carry shorter notice. (https://ai.google.dev/gemini-api/docs/deprecations)
- Implication: do not choose a 2.5 model for a project starting now. Candidate defaults: `gemini-3.5-flash-lite` (cheap, high-volume, no shutdown date) for summary/questions; `gemini-3.8-flash` as the "larger model" fallback in AD-4. Model name stays a setting; add that the setting must be re-checked against the deprecations page and that a 404/"model not found" error should surface as a clear admin message. Dates are "earliest possible"; names above are from the page and I could not cross-check them on a second source.
- Free-tier numbers: Google's rate-limits page gives no numbers (says view them in AI Studio) and does not state which models are free (https://ai.google.dev/gemini-api/docs/rate-limits). Third-party blogs (Jan/Feb 2026) say quotas were cut in Dec 2025 and disagree on RPM; one claims about 1,000 requests/day for 2.5 Flash-Lite and about 20/day for 2.5 Flash. UNCONFIRMED. The spine does not quote numbers, which is correct; keep it that way and read the live limits in AI Studio. Budget check: one 50-slide evaluation (summary, quizzes, 3 essay runs) must fit the per-minute and per-day quota of the chosen model, so AD-13 pacing needs the real numbers before the Test Set size is fixed.
- 429 handling: Google docs say exceeding limits "will trigger a rate limit error" and cite `429 RESOURCE_EXHAUSTED`. In google-genai this surfaces as `google.genai.errors.ClientError` with `code == 429` and `status == "RESOURCE_EXHAUSTED"` (seen in user tracebacks via search; the official errors doc page was not fetched, so the attribute names are from tracebacks, not reference docs). The message can include a suggested retry delay (about 51 s in one report). A `limit: 0` message means no free quota for that model/project, which retrying will not fix; ai_client should distinguish "wait" from "this model is not available to you". AD-4 should say so. 5xx surface as `ServerError`.

### F5 (high) google-genai API surface has changed; spine says "structured output with a schema" without naming how
The current Gemini structured-output docs show a new Interactions API (`client.interactions.create`, `response_format` with `mime_type: application/json` and a JSON schema from Pydantic `model_json_schema()`) rather than `generate_content(config=GenerateContentConfig(response_mime_type=..., response_schema=...))` (https://ai.google.dev/gemini-api/docs/structured-output). The page does not mention `response_schema` at all, and the google-genai release notes (2.31.0) neither deprecate `generate_content` nor mention `response_schema` changes (https://github.com/googleapis/python-genai/releases). So `generate_content` + `response_schema` very likely still works, but this is UNCONFIRMED from official docs I could read. Action: in the AI-client build step, run a 5-line spike for both call styles on the chosen model and pick the documented-current one; keep it inside `ai_client.py` (AD-2 already guarantees that). Also from the docs: supported schema is a JSON Schema subset, large/deeply nested schemas may be rejected, and output is only guaranteed to be syntactically valid JSON, so the AD-4 "validation of the result" is correctly required. Do not use `minItems`/`enum` as a correctness guarantee for "one correct answer"; validate in code (AD-8/AD-13 already do).
Major-version note: google-genai is now 2.x (spine just says "google-genai"); pin exactly, since a 1.x-era tutorial snippet may not match.

### F6 (high, legal/ethics) Free-tier data use: spine is right, add two facts
AD-16 says Google may use free-tier content to improve products: confirmed. The pricing page marks "Used to improve our products: Yes" for free tier. The terms (https://ai.google.dev/gemini-api/terms) add: human reviewers may read and annotate inputs/outputs (disconnected from account/key/project); Google says "Do not submit sensitive, confidential, or personal information to the Unpaid Services"; and in the EEA, Switzerland and the UK the paid-service data terms apply even to unpaid quota (so for Norwegian users, the free tier is covered by paid terms). Consequences: (a) the upload notice should mention human review and the "no sensitive info" advice; (b) the EEA exception is relevant to a Norwegian (HiMolde) course, may make the notice wording partly wrong for users there, and needs a deliberate wording decision rather than a flat "may use your content". I did not verify whether the free-tier terms for EEA also require billing be enabled; third-party blogs claim paid-only for EEA-serving apps, UNCONFIRMED. Recommend a one-line check with the instructor/legal text before the notice is finalised.

### F7 (low) pdfplumber
MIT, 0.11.10, Python >=3.8: AD-9 claim confirmed. Note it pins `pdfminer.six==20260107` exactly and needs Pillow >=12.2 and pypdfium2: pin the whole tree via `pip freeze` in `requirements.txt` (AD-12 says exact versions, fine). PyMuPDF AGPL claim not re-verified (well known, from memory; low risk).

### F8 (low) htmx
"2.x" is still reasonable, but htmx 4.0.0 is now marked Latest on GitHub (2026-08-28). A 2026 student following current docs or `unpkg` "latest" could get 4.x, whose defaults differ from 2.x. Pin the file in the repo as the spine says, and name the exact version (2.0.10, assuming it is the last 2.x; I could not confirm there is no 2.1+) and the htmx.org docs version. Also pair with `django-htmx` only if wanted; not required. Source: https://github.com/bigskysoftware/htmx/releases . Year of the 2.0.10 tag not shown on the page: UNCONFIRMED.

### F9 (low) django-environ
0.14.0 lists Django 5.2 and 6.0 classifiers: AD-12 choice confirmed.

### F10 (low) SQLite
"The version in Python's standard library" is fine. WAL requires SQLite 3.7+, always true. Django 5.2 supports setting `OPTIONS: {"transaction_mode": "IMMEDIATE", "init_command": "PRAGMA journal_mode=WAL;"}` and `timeout`; this was from memory of Django 5.1+ docs, not re-fetched here: UNCONFIRMED, check https://docs.djangoproject.com/en/5.2/ref/databases/#sqlite-notes when writing settings. `IMMEDIATE` transaction mode is the usual fix for "database is locked" under write-after-read.

## Things asserted from memory in the spine (not checked here)
- PyMuPDF is AGPL. (Commonly true; also dual-licensed commercially.)
- Django CSRF applies to htmx requests by default only if the header `X-CSRFToken` is sent (hx-headers); the spine says protection stays on, but should specify how htmx sends the token.
- "Check file type by content" (python-magic or reading `%PDF-` header): fine, no library named.

## Suggested edits to the spine's Stack table
| Name | Suggested text |
| --- | --- |
| Python | 3.13 (3.12 acceptable); not 3.10 (EOL 2026-10-01), not 3.15 until wheels confirmed |
| Django | 5.2 LTS, 5.2.18 at review date; do not move to 6.x |
| django-q2 | 1.11.1 at review date; Windows worker start must be tested first; Q_CLUSTER: workers 1, orm default, timeout < retry, max_attempts 1 to 3 |
| htmx | 2.0.10 file in repo, not 4.x |
| pdfplumber | 0.11.10 |
| google-genai | 2.31.0 (2.x); spike generate_content vs Interactions for structured output |
| django-environ | 0.14.0 |
| Gemini model | setting; start with gemini-3.5-flash-lite, fallback gemini-3.8-flash; not 2.0.x (shut down 2026-06-01), avoid 2.5.x for new work |
