---
type: epic
title: "Foundation and accounts"
parent: initiative-recall
covers: [FR-1, FR-2, SM-7]
after: []
assignee: ""
risk: medium
---

# Foundation and accounts

## Description

The Django project is set up with the email-based custom user model before the first migration, so it never has to be replaced. A visitor can register, log in and log out, and the app guarantees that nobody sees another user's lectures. This epic also holds the platform baseline the other epics lean on: settings from `.env`, the base page, the test setup and the one-command start.

## Outcome

A student can create an account and log in; a test proves a logged-out visitor and a second user get no lecture data (SM-7).

## Done when

1. Registering, logging in and logging out work; a duplicate email is rejected with a clear message and passwords are never stored in plain text (FR-1).
2. A logged-out request to any lecture address redirects to login; another user's lecture id gives the same 404 as a missing id (FR-2).
3. The generated URL-by-user test and the import-boundary test exist and pass (AD-8, AD-2).
4. `python manage.py test` passes with no `.env` and no key (AD-14).
5. `python run.py` starts the app with no `.env` (AD-12, AD-15).

## Boundaries

Accounts, access control and the project baseline. Not upload, not AI, not any lecture content. The Example Lecture exception to FR-2 is built in epic-demo-readme.

## References

- parent — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-1, FR-2, SM-7
- constraint — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-1, AD-2, AD-7, AD-8, AD-12, AD-14, AD-19, AD-24
- design — _bmad-output/initiative-recall/ux-recall/wireframes/01-login.md

## Notes

- Decision: build order step 1 is the custom user model and `AUTH_USER_MODEL`, before the first migration (architecture AD-7; user, 2026-10-18).
- Decision: tracer bullet is story 1: `python run.py` starts the app and the home page opens. Order 1 to 3 is strict: model, login, then privacy (user, 2026-10-18).
- Note: local-only app, so no CI or deployment work in this baseline (architecture AD-15); the base template, CSP and htmx rules (AD-19) are built in story 2.
- Decision: the README is started in story 1 with install and start commands; every later story in every epic adds its own section, and a test checks the list of required headings (user, 2026-10-18).
- Tier: must-have.
