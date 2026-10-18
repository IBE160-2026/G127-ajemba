---
id: 1
type: story
title: "Gemini key, model choice and ai_client with replay mode"
parent: epic-summary
covers: [FR-25]
after: [1.1]
refined: true
hitl: true
risk: high
---

# Gemini key, model choice and ai_client with replay mode

## Description

**Your part (hitl):** create a free Gemini API key in Google AI Studio and put it only in your local `.env`. Then the agent runs a short throwaway test of both ways to ask Gemini for structured output, you and the agent pick the model from Google's current pages, and the choice is recorded. After that `ai_client.py` is built as the only module that talks to Gemini. It can run without a key by replaying stored sample answers, which is how all tests and Demo Mode work. Only your own or freely licensed slides are ever sent during development.

## Acceptance Criteria

1. **The model choice is recorded**
   **Given** the spike results
   **When** the story is done
   **Then** `docs/ai-model-choice.md` states the model name, the date checked, the free-tier limits seen, and which structured-output call style works, and the model name is a setting, never written in code
2. **Only one module knows the provider**
   **Given** the code base
   **When** the import-boundary test runs
   **Then** only `ai_client.py` imports the Gemini library and no other file names the provider
3. **A real key is detected carefully**
   **Given** `GEMINI_API_KEY` empty, only spaces, a known placeholder, or the wrong shape
   **When** the app starts
   **Then** the key counts as missing, no client is ever built, and the app runs in replay mode
4. **Replay needs no key and no network**
   **Given** a stored sample response for a task and an id
   **When** the client is called in replay mode
   **Then** it returns that response with no network access, and an unknown (task, id) fails with a clear error
5. **One call is bounded**
   **Given** the settings `AI_CALL_TIMEOUT_S=60`, `RATE_WAIT_MAX_S=90` and `AI_JOB_BUDGET_S=220`
   **When** a call times out, or waits for a rate limit longer than allowed, or the job budget ends
   **Then** the call ends as failed with the plain FR-5 message, and an answer saying free quota is zero for the model ("limit: 0") is not retried
6. **Usage is logged without content**
   **Given** any call
   **When** it finishes
   **Then** one `AiCallLog` row holds task, model, prompt version, approximate token counts, wait time and user id, and no lecture or essay text appears in it or in the log files
7. **The rate budget is shared**
   **Given** the web app and the worker
   **When** both read the minute and day counters
   **Then** they use one `RateLimitState` row updated in a short transaction
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Using your own Gemini key" section says where to get a free key, that it goes only in the local `.env`, which setting names the model, and that without a key the app runs in Demo Mode

## Tests

- `test_readme_has_required_sections` (adds "Using your own Gemini key" to the list)
- `test_fr25_only_ai_client_imports_gemini` (part of the import-boundary test)
- `test_key_detection_placeholder_and_empty`
- `test_replay_returns_stored_response_without_network`
- `test_ai_call_log_has_no_content`
- `test_quota_zero_error_is_not_retried`
- Manual by you: spike script run and `docs/ai-model-choice.md`

## Boundaries

- Must not change: nothing in upload or accounts. No prompts or validators here (story 3). No call from a web request, only from jobs (AD-4.2).

## References

- parent — _bmad-output/initiative-recall/epic-summary/epic-summary.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-4, AD-5.11, AD-12.2, AD-14, Stack and Deferred sections
- terms — _bmad-output/initiative-recall/architecture-recall/gemini-terms-checked-2026-10-17.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-25

## Notes

- Unknown: current Gemini model names and free-tier limits; settled during this story from Google's pages, not from memory.
- Assumption: if the whole story does not fit in 2 hours, split the spike and the model note from the client.
