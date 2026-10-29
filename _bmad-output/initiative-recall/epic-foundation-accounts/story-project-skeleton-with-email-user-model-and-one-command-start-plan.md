---
title: 'Project skeleton with email user model and one-command start'
type: 'feature'
ticket: 'story-project-skeleton-with-email-user-model-and-one-command-start'
created: '2026-10-29'
status: 'built'
baseline_revision: 'c2745492392d921e93c11d066b0d038bf68f2cad'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: [self-review]
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The repo has no application. Every later story needs a Django project whose user model is the email-based custom model from the first migration, plus a start command that works on Windows.

**Approach:** Create the thinnest working Django 5.2 app (story AC 1-8): `config` project, `accounts` app with the `User` model, settings read only in `settings.py` via django-environ, safe SQLite options, `run.py`, home page, git hygiene files, README section, and the five named tests.

## Boundaries & Constraints

**Always:** Custom `accounts.User` (login field `email`) and `AUTH_USER_MODEL` exist before any `makemigrations`/`migrate`. Pinned `Django==5.2.18`, `django-environ==0.14.0`; Python 3.12/3.13 only. Environment is read only in `config/settings.py` (AD-12). Tests need no `.env` and no key (AD-14). Windows commands first. Test names/comments cite the AC/FR.

**Never:** No login pages, lecture tables, AI code, django-q2 or WhiteNoise (added when needed, per story note). No `django.contrib.admin`. No commit, no push. No default `SECRET_KEY` when `RECALL_ENV` is not `local`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Email normalised | `"  Amara@Example.com "` | stored `amara@example.com` | — |
| Duplicate email | second user `AMARA@example.com` | `IntegrityError` from the unique index | — |
| Fresh start | no `.env`, `python run.py` | migrate runs, server on localhost, `/` returns 200 | — |
| Wrong Python | Python not 3.12/3.13 | stops, plain message naming 3.12 and 3.13 | exit code 1 |
| Unsafe settings | `RECALL_ENV=production`, no `SECRET_KEY` | stops with a clear message | `ImproperlyConfigured` |

</frozen-after-approval>

## Code Map

Repo root has no code yet (only docs, `_bmad*`, `README.md`, `.gitignore`). Everything below is new unless marked.

- `manage.py`, `config/{__init__,settings,urls,wsgi,asgi,views}.py` -- project; `settings.py` is the only reader of the environment
- `accounts/{__init__,apps,models,managers,tests}.py`, `accounts/migrations/0001_initial.py` -- custom `User`
- `templates/home.html` -- home page
- `run.py` -- version check, `migrate`, then `runserver --noreload`
- `requirements.txt`, `.env.example` -- exact pins; every setting commented, no keys
- `.gitignore` (edit: add `db.sqlite3*`, `logs/`), `.gitattributes` -- `*.md`, `*.json`, `*.txt` as `text eol=lf`
- `README.md` (edit: append "Install and start"), `docs/required_readme_headings.txt` -- first line "Install and start"
- `config/tests.py` -- settings, SQLite, README and git tests

## Tasks & Acceptance

**Execution:**
- [ ] `requirements.txt`, `.env.example`, `.gitignore`, `.gitattributes` -- pins and hygiene -- AC 6
- [ ] `accounts/models.py`, `accounts/managers.py` -- `User(AbstractBaseUser, PermissionsMixin)`, `USERNAME_FIELD="email"`, unique email, strip+lower in manager and `save()`, `notice_ack_at`, `notice_version` (AD-7/AD-17) -- AC 1, 2
- [ ] `config/settings.py` -- `AUTH_USER_MODEL="accounts.User"` set before first `makemigrations`; django-environ; `DEBUG` only for `RECALL_ENV` unset/`local`; refuse missing `SECRET_KEY` otherwise; `ALLOWED_HOSTS` default `localhost,127.0.0.1`; SQLite `OPTIONS` (`timeout` 20, `transaction_mode` IMMEDIATE, `init_command` WAL/NORMAL/foreign_keys); logging to `logs/web.log` -- AC 5, 7
- [ ] `config/urls.py`, `config/views.py`, `templates/home.html` -- home page at `/` -- AC 3
- [ ] `run.py` -- check Python and Django are present, run migrate, start server; no shell-specific syntax -- AC 3, 4
- [ ] `README.md`, `docs/required_readme_headings.txt` -- section -- AC 8
- [ ] `accounts/tests.py`, `config/tests.py` -- `test_fr1_email_is_normalised_and_unique`, `test_settings_refuse_missing_secret_when_not_local`, `test_sqlite_pragmas_set`, `test_env_file_not_tracked_by_git`, `test_readme_has_required_sections`, home returns 200 -- AC 1, 2, 5-8
- [ ] User (hitl): create the venv, install requirements, run the manual checks for AC 3 and 4

**Acceptance Criteria:**
- Given the 8 story criteria, when `python manage.py test` runs with no `.env` then all tests pass, and the manual checks for AC 3 and 4 succeed.

## Implementation Notes

## Plan Change Log

## Review Triage Log

Self-review by the implementing session (no independent reviewer subagent was run). 0 high, 0 medium, 3 low.

- low, not fixed -- `User.objects.bulk_create(...)` bypasses `save()`, so email normalisation would not run. No code uses `bulk_create` on users; fix would add surface. Revisit if one appears.
- low, not fixed -- `ALLOWED_HOSTS=` (empty in `.env`) gives `[]`. With `DEBUG` on Django still allows localhost; with `DEBUG` off every request is refused loudly. Not a silent failure.
- low, not fixed -- `README.md` had CRLF line endings; `.gitattributes` now forces LF, so git may print a "CRLF will be replaced by LF" warning at the next commit. Harmless.
- Verified OK: all 8 criteria (tests 10/10, manual start gave HTTP 200 with no `.env`, wrong-Python message and exit code 1, git ignores `.env`, `db.sqlite3`, `logs/`); no migration used the default user model.

### Found by the user's manual test, not by the self-review (2026-10-29)

- **high, fixed** -- `run.py`: after Ctrl+C on Windows the server kept running and `http://localhost:8000/` still loaded. This breaks AD-15.1 (Ctrl+C stops everything). The self-review above missed it; it only looked at the diff and my own start/stop test, which ended the server by killing processes by hand.
- **Cause, as the user identified it:** the `.venv` launcher on Windows. Every `.venv\Scripts\python.exe` is a small launcher that starts the real Python as a child, so the tree was `run.py` (launcher) -> `run.py` (real) -> `runserver` (launcher) -> `runserver` (real). Confirmed from the process list found after the failure: all four were alive, and `run.py` itself had not exited.
- **Verified by testing:** (1) if `run.py` disappears without cleaning up, the server keeps running and answers 200 (two orphaned `runserver` processes). (2) The old `run.py` waited with `subprocess.call`, which on Windows cannot be woken by Ctrl+C, so `run.py` only ended if the server ended by itself.
- **Not reproduced:** a real Ctrl+C alone, sent to a hidden console in four situations (plain, idle connections, half-finished request, keep-alive), stopped everything correctly with the old code. So the exact trigger on the user's machine is not proven; the user's attribution to the launcher layering is consistent with the process list but I could not isolate it.
- **Fix (`run.py`):** (a) wait in 0.2 s rounds so Ctrl+C always reaches `run.py`; (b) on Ctrl+C or Ctrl+Break give the server 3 s to stop, then `taskkill /F /T` the whole tree; (c) a Windows job object (`KILL_ON_JOB_CLOSE`) so every process `run.py` started dies when `run.py` ends, even if it is killed. Added `--port` so a test can use a free port.
- **Tests added** (`config/tests.py`, Windows only): `test_server_dies_when_run_py_is_killed`, `test_ctrl_break_stops_run_py_and_server`. Full suite: 12 tests OK. A real Ctrl+C needs a console and is a manual check (see Verification).
- **Result:** the user repeated the manual browser test after the fix: after Ctrl+C, Firefox cannot connect to `localhost:8000`.

## Design Notes

- Settings test runs a subprocess with `RECALL_ENV_FILE` pointing to a missing file, so a developer's own `.env` cannot hide the failure.
- django-q2 and WhiteNoise are deferred (story note: add when needed; q2 in epic-summary story 2). This means static files rely on `DEBUG` for now; there are none yet.

## Verification

**Commands:**
- `python manage.py check` -- expected: no issues
- `python manage.py makemigrations --check` -- expected: no changes
- `python manage.py test` -- expected: all pass, with no `.env`
- `git status --short` -- expected: no `.env`, `db.sqlite3` or `logs/`

**Manual checks (if no CLI):**
- `python run.py` with no `.env`, open http://localhost:8000/ and see the home page
- Wrong-Python refusal: run `run.py` with a Python that is not 3.12/3.13, see the message
- Ctrl+C stops everything (AD-15.1), in a normal Windows terminal: start `python run.py`, open http://localhost:8000/ in the browser and leave the tab open, press Ctrl+C in the terminal, wait about 3 seconds, reload the page. Expected: the terminal prompt returns and the browser says it cannot connect. Then check that no `python.exe` from `.venv` is left in Task Manager.
