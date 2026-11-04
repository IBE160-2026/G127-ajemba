---
title: 'Register, log in and log out'
type: 'feature'
ticket: 'story-register-log-in-and-log-out'
created: '2026-11-04'
status: 'built'
baseline_revision: 'bf08b43d9bb60a0336f416c36175eb3a7fe54f21'
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

**Problem:** Visitors cannot create an account, log in or log out, and there is no shared base page with the web-safety rules (AD-19). Later stories need both.

**Approach:** Add register, log-in and log-out on Django's built-in auth and the story 1.1 email user model (story AC 1-9). Add a base template with CSRF header for htmx, a content security policy, `no-store` for logged-in pages, a database-backed login-failure limit, and a vendored htmx 2.0.10.

## Boundaries & Constraints

**Always:** Use `django.contrib.auth` (`LoginView`, `LogoutView`, `login()`), `url_has_allowed_host_and_scheme` for `next`, Django's default password validators and the unchanged `accounts.User`. Logout is POST only. Every state-changing action is POST. htmx is a file in `static/`, never loaded from a network, with its source, version and SHA-384 recorded beside it. No inline scripts or styles (CSP). Tests need no `.env` and no key; test names cite FR/AC. Plain English messages. Failure messages never say whether the email exists.

**Never:** No email verification, no password reset, no "Try the demo" button. Do not change the user model or email rules. No lecture table (story 1.3). No new dependency. No commit, no push.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Register | new email, strong password | account exists, logged in, redirect `/lectures/` | — |
| Duplicate email | `Amara@Example.com` when `amara@example.com` exists | no second account | "This email is already in use. Log in, or use another." |
| Weak password | `password` or 4 characters | refused | validator's own message |
| 6th login | 5 failures in 15 min, same email + address, correct password | refused, no login | "Too many failed log-in attempts. Try again in 15 minutes." |
| After 15 min | fixed clock moved 15 min | login works | — |
| Other address | same email from another address | counted separately | — |
| Unsafe `next` | `next=https://evil.example/` | redirect `/` | — |
| Safe `next` | `next=/lectures/` | redirect `/lectures/` | — |
| Logout via GET | GET `/accounts/logout/` | stays logged in | 405 |
| Logged out | GET `/lectures/` | redirect `/accounts/login/?next=/lectures/` | — |

</frozen-after-approval>

## Code Map

Existing: `config/settings.py` (add cache, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, middleware), `config/urls.py`, `config/views.py`, `templates/home.html` (make it extend the base), `run.py:124` (add `createcachetable` after `migrate`), `config/tests.py` (`test_readme_has_required_sections`), `docs/required_readme_headings.txt`, `README.md`. Do not touch `accounts/models.py` or `accounts/managers.py`.

New:
- `accounts/{forms,views,urls,throttle}.py` -- register form, views, login limit
- `config/middleware.py` -- CSP header and `Cache-Control: no-store` for logged-in responses
- `templates/{base.html,lectures.html,accounts/login.html,accounts/register.html}`
- `static/vendor/htmx.min.js` plus `htmx.SOURCE.txt` (source, version, SHA-384)
- `static/js/logout.js` -- on logout form submit, remove `localStorage` keys starting with `recall:` or `htmx-history-cache`
- `static/css/recall.css` -- minimal styling

## Tasks & Acceptance

**Execution:**
- [ ] `static/vendor/htmx.min.js`, `htmx.SOURCE.txt` -- copy checked file from the official tag v2.0.10; hash equals the one in htmx's README -- AC 8
- [ ] `config/settings.py` -- `CACHES` database cache (`recall_cache`, `MAX_ENTRIES` 10000 so filler keys cannot evict counters, timeout a little over 15 min), `LOGIN_URL`, `LOGIN_REDIRECT_URL="/"`, `LOGOUT_REDIRECT_URL`, `STATICFILES_DIRS`, middleware, accounts app templates -- AC 5-8
- [ ] `accounts/throttle.py` -- failures kept per hash(email + address) with timestamps, `now()` replaceable in tests; 5 in 15 min blocks; success clears -- AC 5
- [ ] `accounts/forms.py`, `views.py`, `urls.py` -- register (validate password, case-insensitive duplicate check, `login()`), login with limit, logout POST only -- AC 1-7
- [ ] `config/middleware.py` -- CSP exactly as in AD-19, `no-store` when logged in -- AC 6, 8
- [ ] `templates/*`, `static/js/logout.js`, `static/css/recall.css` -- base page with `hx-headers` CSRF on `<body>`, htmx config in a `<meta name="htmx-config">` tag (the three story settings plus `includeIndicatorStyles:false`, since the CSP blocks htmx's inline style), nav with POST logout form; `/lectures/` placeholder behind `login_required` -- AC 1, 6, 8
- [ ] `run.py` -- run `createcachetable` after `migrate` -- AC 5
- [ ] `README.md`, `docs/required_readme_headings.txt` -- "Accounts" section (register, log in, log out; no email check, no password reset in v1) -- AC 9
- [ ] `accounts/tests.py`, `config/tests.py` -- the 7 tests named in the story, plus I/O matrix cases (other address, 15 min later, GET logout, safe `next`), htmx hash test, `logout.js` names both key prefixes (the real clearing is a manual browser check) -- AC 1-9

**Acceptance Criteria:**
- Given the 9 story criteria, when `python manage.py test` runs with no `.env`, then all tests pass, and the manual browser test succeeds.

## Implementation Notes

Built directly in the session (no coding subagent; the user did not ask for subagents). Files: `accounts/{forms,views,urls,throttle}.py`, `config/{middleware,settings,urls,views}.py`, `templates/{base,home,lectures}.html`, `templates/accounts/{login,register}.html`, `static/{vendor/htmx.min.js,vendor/htmx.SOURCE.txt,js/logout.js,css/recall.css}`, `run.py`, `README.md`, `docs/required_readme_headings.txt`, `accounts/tests.py`, `config/tests.py`.
- htmx 2.0.10 came from tag v2.0.10 of `bigskysoftware/htmx`; its SHA-384 equals the hash in that tag's README (checked 2026-11-04).
- Django's `LoginView` already applies `never_cache`, so the log-in page is `no-store` even when logged out. Harmless; the test uses the home page for the logged-out case.
- The log-in form lower-cases and strips the email itself, because `get_by_natural_key` matches exactly and the user model must not change.
- Ran the real server on port 8012: `/`, login, register, htmx, js and css returned 200, `/lectures/` returned 302 to login, CSP header present. Server stopped, port closed.

## Plan Change Log

## Review Triage Log

Self-review by the implementing session (no independent reviewer subagent was run, so this is weaker than a separate review). 0 high, 0 medium, 2 low. 28 tests OK, `check` and `makemigrations --check` clean.

- low, not fixed -- Registration has no attempt limit (only login does). The story and AD-7 limit login only. Revisit if abuse matters.
- low, not fixed -- The wireframe's "Show password" checkbox is not built. It is not in the story criteria and needs a static script. Left for a later story.
- Verified OK: all 9 criteria and all 10 rows of the I/O matrix are covered by tests that ran; logout needs POST; unsafe `next` goes to `/`; the limit is per email plus address and counts unknown emails the same way.

## Design Notes

- Limit key is a hash of `email|REMOTE_ADDR`, so an unknown email is limited the same way (no account leak).
- Registered and logged-in users on `/accounts/login/` are redirected on.
- `/lectures/` is a placeholder; story 1.3 and epic-summary replace its content. It is the page AC 1 and AC 6 need.
- The check-then-count step in the limit is not atomic; two simultaneous failures could let one extra try through. Accepted for a local single-user app.
- Static files are served only while `RECALL_ENV` is `local` (WhiteNoise deferred in story 1.1); the README says so.
- JavaScript for clearing storage lives in a static file because the CSP forbids inline scripts.

## Verification

**Commands:**
- `python manage.py check` -- expected: no issues
- `python manage.py makemigrations --check` -- expected: no changes
- `python manage.py test` -- expected: all pass, no `.env`
- `git status --short` -- expected: only intended files, no `.env` or `db.sqlite3`

**Manual checks (if no CLI):**
- Browser: register, log out, log in, wrong password 6 times, open `/lectures/` logged out.
