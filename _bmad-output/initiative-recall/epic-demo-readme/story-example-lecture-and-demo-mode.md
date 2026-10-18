---
id: 1
type: story
title: "Example Lecture and Demo Mode"
parent: epic-demo-readme
covers: [FR-23, SM-9]
after: [4.3]
refined: true
hitl: true
risk: medium
---

# Example Lecture and Demo Mode

## Description

Anyone can open a prepared Example Lecture without a key or an account and use the same screens as the real app, so the examiner can try Recall straight away. **Your part (hitl):** generate the example with your real key from your own deck (test lecture 1) or a freely licensed deck, read the Summary and questions yourself, and save the result with its provenance in `example_lecture.json`. In this story Demo Mode covers the Summary and Multiple Choice; Fill-in and Essay add their own demo content later.

## Acceptance Criteria

1. **The example comes from reviewed data**
   **Given** `example_lecture.json`
   **When** it is opened
   **Then** it holds the Summary, key terms and Multiple Choice questions of a real AI run you reviewed, plus date, model, prompt versions, reviewer and review notes, and no course material from lecturers
2. **Loading is safe to repeat**
   **Given** `manage.py load_example`
   **When** it runs twice, and `run.py` runs it before starting
   **Then** exactly one Example Lecture exists (unique `example_key`, one IMMEDIATE transaction)
3. **No key means Demo Mode**
   **Given** no `GEMINI_API_KEY`
   **When** the app starts
   **Then** it starts, the login page shows a clear banner, and uploading shows "Processing needs an API key. See the README."
4. **The demo button is always there**
   **Given** the login page with or without a key
   **When** a visitor presses Try the demo
   **Then** the Example Lecture opens with no registration or login
5. **The banner names the limits**
   **Given** any page of the Example Lecture
   **When** it loads
   **Then** a banner says only the example lecture is available, essay feedback is prepared in advance, and uploading and free-text essay assessment need an API key
6. **The example is read-only and public**
   **Given** the Example Lecture
   **When** anyone requests it, or tries to edit or delete it
   **Then** reading works for everyone (the only exception to the privacy rule), and every write is refused with the shared 404
7. **Progress stays in the browser session**
   **Given** a visitor taking the quiz on the example
   **When** they answer questions
   **Then** progress is kept only in the server-side session under `demo_progress` through the same interface as the database store, no Attempt or Answer row is written, and `Attempt.user` stays NOT NULL
8. **The example never reaches the AI**
   **Given** an example lecture, even with a real key set
   **When** any action runs on it
   **Then** `ai_client` is never called (a test with a spy that raises), and real uploads with a key still work
9. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Demo Mode" section says how to start without a key, what the demo can do and what it cannot (uploading and free-text essay assessment need a key), and what the banner means

## Tests

- `test_readme_has_required_sections` (adds "Demo Mode" to the list)
- `test_fr23_app_starts_without_key`
- `test_fr23_try_demo_opens_example_without_login`
- `test_fr23_banner_on_every_example_page`
- `test_fr23_upload_without_key_shows_needs_key_message`
- `test_ad10_example_lecture_never_calls_ai_client`
- `test_ad10_load_example_is_idempotent`
- `test_fr2_example_is_public_but_read_only`
- `test_demo_progress_stored_in_session_only`

## Boundaries

- Must not change: privacy rules for real lectures (the example is the only exception). No new quiz types.

## References

- parent — _bmad-output/initiative-recall/epic-demo-readme/epic-demo-readme.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-10, AD-12.4, AD-17 (example rows)
- design — _bmad-output/initiative-recall/ux-recall/EXPERIENCE.md (Demo Mode banner, Flow 2); wireframes/01-login.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-2, FR-23, SM-9

## Notes

- Handoff: epic-multiple-choice-results story 2 provides the `ProgressStore` interface and its database implementation; this story adds the session implementation behind the same interface.
- Assumption: the example is built from your own deck, so provenance names you as author and reviewer.
