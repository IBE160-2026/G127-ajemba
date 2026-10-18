---
id: 3
type: story
title: "Lectures are private to their owner"
parent: epic-foundation-accounts
covers: [FR-2, SM-7]
after: [2]
refined: true
hitl: false
risk: high
---

# Lectures are private to their owner

## Description

A minimal Lecture table is added with one rule for reaching it: every view gets lectures only through an owner-scoped manager, and every wrong user, missing id or write to an example lecture gets the same 404. Two guard tests are created that protect every later epic: one that requests every address as the wrong user, and one that checks the import rules. The Example Lecture exception is added later in epic-demo-readme.

## Acceptance Criteria

1. **Owner-scoped access**
   **Given** a lecture owned by user A
   **When** user A requests it through `Lecture.objects.for_user(A)`
   **Then** it is found, and `for_user(B)` does not find it
2. **Other users and missing ids look the same**
   **Given** a lecture of user A
   **When** user B requests it by id, and when anyone requests an id that does not exist
   **Then** both responses are the same 404 page with no lecture data
3. **Logged-out visitors get nothing**
   **Given** a logged-out visitor
   **When** they request any lecture address
   **Then** they are redirected to login and the response contains no lecture data
4. **Writes go through one door**
   **Given** a lecture marked as an example
   **When** a mutating endpoint calls `get_lecture_for_write(user, id)`
   **Then** it is refused with the same 404
5. **Every address is tested automatically**
   **Given** the list of addresses in `urls.py`
   **When** the generated test requests each one as user B with user A's ids and as a logged-out visitor
   **Then** none returns lecture data, and a newly added address is covered without editing the test
6. **Import rules are enforced**
   **Given** the modules in `core/` and the rule that only `ai_client.py` imports the Gemini library, only `pdf_text.py` imports pdfplumber, and only `jobs.py` imports django-q2
   **When** the import-boundary test runs
   **Then** it passes, and it fails on a deliberately broken example module (included in the test)
7. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Privacy rules" section says each user sees only their own lectures, that the Example Lecture is the one public exception added later, and what the two guard tests check

## Tests

- `test_readme_has_required_sections` (adds "Privacy rules" to the list)
- `test_sm7_user_b_cannot_read_user_a_lecture`
- `test_sm7_logged_out_gets_redirect_and_no_data`
- `test_fr2_every_url_as_other_user_and_anonymous` (generated from `urls.py`)
- `test_ad2_import_boundaries` plus `test_ad2_import_boundaries_detects_violation`

## Boundaries

- Must not change: login and register behaviour from story 2. No upload, no AI code, no Example Lecture exception yet.

## References

- parent — _bmad-output/initiative-recall/epic-foundation-accounts/epic-foundation-accounts.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-2, AD-8, AD-10.5, AD-17 (Lecture row), AD-18.2
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-2, SM-7

## Notes

- A small stub lecture detail page is added so the tests have something to request; it is replaced by the real Summary page in epic-summary.
