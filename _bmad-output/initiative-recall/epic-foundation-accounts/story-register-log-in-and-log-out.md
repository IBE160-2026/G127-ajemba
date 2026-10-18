---
id: 2
type: story
title: "Register, log in and log out"
parent: epic-foundation-accounts
covers: [FR-1]
after: [1]
refined: true
hitl: false
risk: medium
---

# Register, log in and log out

## Description

A visitor can register with an email and password, log in, and log out, using Django's built-in login system on the custom user model. The base page template is created here, with the HTMX token header, so later pages share it. Five failed logins in 15 minutes for the same account and address block further tries.

## Acceptance Criteria

1. **Registering works**
   **Given** a visitor on the register page
   **When** they submit a new email and a password that passes Django's validators
   **Then** an account exists, they are logged in, and they land on the My lectures page
2. **A used email is rejected**
   **Given** an account for `amara@example.com`
   **When** someone registers `Amara@Example.com`
   **Then** no second account is created and the page shows a clear message that the email is already in use
3. **Passwords are never stored in plain text**
   **Given** a registered user
   **When** the user row is read from the database
   **Then** the stored password is a hash and does not contain the password
4. **Weak passwords are refused**
   **Given** the register page
   **When** the password is too common or too short
   **Then** it is refused with the validator's plain message
5. **Login throttle**
   **Given** an account and an address that failed login 5 times in the last 15 minutes
   **When** a 6th login is tried, even with the correct password
   **Then** it is refused with a clear message and succeeds again after 15 minutes
6. **Logout ends access**
   **Given** a logged-in user
   **When** they log out with a POST request
   **Then** a saved-lecture page redirects to login, a GET to the logout address does not log out, and logged-in responses carry `Cache-Control: no-store`
7. **Safe redirect**
   **Given** a login request with `next` pointing to another site
   **When** login succeeds
   **Then** the user is sent to the home page, not to the other site

8. **The base page is safe for HTMX**
   **Given** the base template
   **When** any page loads
   **Then** the CSRF token is sent with every HTMX request through `hx-headers` on `<body>`, the content security policy is `default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'`, htmx 2.0.10 is a file kept in `static/` (never loaded from a network) with `allowEval=false`, `selfRequestsOnly=true` and `historyCacheSize=0`, and logout clears every `localStorage` key starting with `recall:` and `htmx-history-cache`
9. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** an "Accounts" section says how to register, log in and log out, and that there is no email check and no password reset in v1

## Tests

- `test_readme_has_required_sections` (adds "Accounts" to the list)
- `test_fr1_register_rejects_duplicate_email`
- `test_csp_header_and_csrf_header_on_base_page`
- `test_fr1_password_is_hashed`
- `test_fr1_login_blocked_after_five_failures` (uses a fixed clock)
- `test_fr1_protected_page_redirects_after_logout`
- `test_logout_requires_post`, `test_login_next_must_be_same_host`

## Boundaries

- Must not change: the user model and email rules from story 1. No email verification and no password reset (PRD §8.2). The "Try the demo" button is added in epic-demo-readme.

## References

- parent — _bmad-output/initiative-recall/epic-foundation-accounts/epic-foundation-accounts.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-7, AD-19
- design — _bmad-output/initiative-recall/ux-recall/wireframes/01-login.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-1

## Notes

- Assumption: the throttle uses Django's database-backed cache and keys on email plus address, as AD-7 says.
