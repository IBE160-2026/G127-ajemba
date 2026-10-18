---
id: 1
type: story
title: "Project skeleton with email user model and one-command start"
parent: epic-foundation-accounts
covers: [FR-1]
after: []
refined: true
hitl: true
risk: medium
---

# Project skeleton with email user model and one-command start

## Description

This is the tracer bullet: the thinnest working app. It creates the Django project with the email-based custom user model before the first migration, settings read from `.env`, SQLite with the safe settings, the test runner, and `run.py`. When it is done you run one command and see a page in your browser. **Your part (hitl):** install Python 3.12 or 3.13, create the virtual environment and install the requirements; the agent cannot do this on your machine.

## Acceptance Criteria

1. **The user model comes first**
   **Given** a repository with no migrations
   **When** the first migration is created
   **Then** `AUTH_USER_MODEL` already points to the custom user model, its login field is the email address, and no migration exists that used Django's default user model
2. **Emails are stored in one form**
   **Given** the custom user model
   **When** a user is created with the email `  Amara@Example.com `
   **Then** it is stored as `amara@example.com`, and creating a second user with `AMARA@example.com` fails on the database unique index
3. **One command starts the app**
   **Given** a fresh clone with no `.env` file
   **When** you run `python run.py`
   **Then** `migrate` runs, the web app starts on localhost, and the home page returns 200 in the browser
4. **Wrong Python is refused**
   **Given** a Python that is not 3.12 or 3.13
   **When** you run `python run.py`
   **Then** it stops with a plain message naming the supported versions
5. **Unsafe settings are refused**
   **Given** `RECALL_ENV` is set to anything other than `local` and `SECRET_KEY` is missing
   **When** the app starts
   **Then** it stops with a clear message instead of using a default key
6. **Git keeps secrets and data out**
   **Given** the repository
   **When** `git status` is run after the app has started
   **Then** `.env`, `db.sqlite3` and `logs/` are ignored, `.gitattributes` marks `*.md`, `*.json` and `*.txt` as `text eol=lf`, and `requirements.txt` has exact versions
7. **SQLite is configured safely**
   **Given** a running app
   **When** a database connection opens
   **Then** WAL mode, `synchronous=NORMAL` and `foreign_keys=ON` are set, with a timeout of 20 seconds and IMMEDIATE transactions
8. **The README is started**
   **Given** the repository
   **When** this story is done
   **Then** `README.md` has an "Install and start" section with Windows commands first, the Python 3.12 or 3.13 check, creating the virtual environment, installing `requirements.txt`, `python run.py` and `python manage.py test`, and a test reads a list of required README headings that starts with this one and that every later story extends

## Tests

- `test_readme_has_required_sections` (the list starts with "Install and start")
- `test_fr1_email_is_normalised_and_unique` (criteria 1, 2)
- `test_settings_refuse_missing_secret_when_not_local` (criterion 5)
- `test_sqlite_pragmas_set` (criterion 7)
- `test_env_file_not_tracked_by_git` (criterion 6; skips with a message if git is missing)
- Manual check by you for 3 and 4; `python manage.py test` passes with no `.env`

## Boundaries

- Must not change: nothing exists yet. Do not add login pages, lecture tables or AI code in this story.

## References

- parent — _bmad-output/initiative-recall/epic-foundation-accounts/epic-foundation-accounts.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-1, AD-7, AD-12, AD-15, AD-24, Stack table
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-1

## Notes

- Decision: build order step 1 is the custom user model before any migration (2026-10-18).
- Open question: whether django-q2 and WhiteNoise are added now or in the stories that need them; default is when needed (epic-summary story 2 for django-q2).
