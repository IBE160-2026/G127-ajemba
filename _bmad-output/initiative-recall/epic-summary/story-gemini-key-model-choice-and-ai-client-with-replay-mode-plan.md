---
title: 'Gemini key, model choice and ai_client with replay mode'
type: 'feature'
ticket: '1'
created: '2026-11-25'
status: 'built'
baseline_revision: '066c1f953723d0ee65a470d27a758e13bc5c698c'
route: 'full'
route_source: 'auto'
risk: 'high'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: ['{project-root}/_bmad-output/initiative-recall/architecture-recall/architecture-recall.md', '{project-root}/_bmad-output/initiative-recall/architecture-recall/gemini-terms-checked-2026-10-17.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Nothing yet talks to Gemini. The model, the structured-output style and the free-tier limits are unknown, and the key must never leak.

**Decisions (user, 2026-11-25):** Model `gemini-3.5-flash-lite`, documented fallback `gemini-3.1-flash-lite` (untested). Structured output uses the JSON-schema style (`response_json_schema`); the Pydantic-class style is not used. Free-tier limits from the user's AI Studio page: 15 per minute, 250K tokens per minute, 500 per day. `google-genai==2.31.0` and its 20 dependencies are pinned in `requirements.txt` (certifi is MPL-2.0, accepted). A 503 or 429 gets one short wait and one retry, then a clear error the job turns into a calm user message; never a crash, never the key.

**Approach:** Build `core/ai_client.py` as the only provider module, with key detection, replay mode, bounds, usage log and a shared rate row. Spike two structured-output styles with the user's own test lecture, then the user chooses the model and it is recorded.

## Boundaries & Constraints

**Always:** The key is read only by `settings.py` from `GEMINI_API_KEY`; the agent never opens, prints, greps or copies `.env`. The model is a setting. Every real call writes one `AiCallLog` row with `local_day`; no lecture text in rows or logs. Install only into `.venv` after the user's yes on PyPI facts. Python is `.venv/Scripts/python`. Only the user's own `evaluation/testset/test-lecture-1.pdf` is sent. Tests need no key and no network.

**Never:** No prompts or validators (story 3.3). No call from a web request. No commit. No change to upload or accounts. No other file names the provider.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Key missing | empty, spaces, placeholder, wrong shape | counts as missing, no client built, replay | none |
| Replay hit | stored (task, id) | stored response, no network | none |
| Replay miss | unknown (task, id) | clear error | `AiReplayMissing` |
| Quota zero | answer contains "limit: 0" | not retried, failed with FR-5 message | `AiCallFailed` |
| Server busy | 503 or 429 (no "limit: 0") | one short wait, one retry, then failed with the FR-5 message | `AiCallFailed`, no key in text |
| Bound hit | timeout, wait over `RATE_WAIT_MAX_S`, budget `AI_JOB_BUDGET_S` over | failed with FR-5 message | `AiCallFailed` |

</frozen-after-approval>

## Code Map

- `config/settings.py` -- add `GEMINI_API_KEY`, `GEMINI_MODEL`, `AI_CALL_TIMEOUT_S=60`, `RATE_WAIT_MAX_S=90`, `AI_JOB_BUDGET_S=220`, `MAX_PROMPT_CHARS`; key detection result as a setting, never the key in logs
- `.env.example` -- add `GEMINI_API_KEY=` (empty) and `GEMINI_MODEL`, with comments; `.env` already ignored (`.gitignore:42`)
- `lectures/models.py:101` -- `AiCallLog` exists (3.2) with `local_day`; add `RateLimitState` + migration 0005; `lectures/services.py:83` `local_today()` gives `local_day`
- `core/tests.py:20` -- import-boundary rule for `google.genai` -> `core/ai_client.py` exists; no file may name the provider
- `config/tests.py:112`, `docs/required_readme_headings.txt` -- add "Using your own Gemini key"
- `core/jobs.py` -- only caller later; do not change
- `evaluation/testset/test-lecture-1.pdf` -- the only spike input, via `core/pdf_text.py`

## Tasks & Acceptance

**Execution:**
- [ ] `.env.example`, `config/settings.py` -- add settings and key detection -- AC3
- [ ] `lectures/models.py` + migration -- `RateLimitState` single row, short transaction -- AC7
- [ ] `core/ai_client.py` -- `call(task, id, ...)`: replay, real call, bounds, "limit: 0", logging, shared rate row -- AC2, 4-7
- [ ] `core/sample_responses/` -- stored sample answers for tests -- AC4
- [ ] `core/test_ai_client.py` -- the six named tests, bounds, and replayed 503 and 429 (one retry, then a calm error, no key in text) -- AC3-6
- [x] `evaluation/spike_gemini.py` + `docs/ai-model-choice.md` -- done: JSON-schema style on 3.5 Flash Lite, two calls logged -- AC1
- [ ] `README.md`, `docs/required_readme_headings.txt` -- "Using your own Gemini key" -- AC8

**Acceptance Criteria:**
- Given the spike results, when done, then `docs/ai-model-choice.md` holds model, date, limits and working style
- Given the code base, when the boundary test runs, then only `ai_client.py` imports the Gemini library
- Given an empty or placeholder key, when the app starts, then replay mode and no client
- Given each real spike call, when it ends, then one `AiCallLog` row with `local_day` exists

## Implementation Notes

## Plan Change Log

## Review Triage Log

Pass 1 (quick): 13 findings. Verdicts: 1 high (found by me, not the reviewer), 3 medium, 5 low, 3 false, 1 maybe-false.

| # | Finding | Verdict | Route | Evidence |
|---|---------|---------|-------|----------|
| 0 | Real key rejected by the shape rule (`.` not allowed) | high | patch | `GEMINI_KEY_PRESENT` was False for the user's real key; shape now allows `. ~`; placeholder rule is by prefix. Now True. |
| 1 | Import direction ai_client -> lectures | low | rejected | Function-level imports, no real cycle (services imports pdf_text, not ai_client); AD-4.3 gives ai_client the usage log. |
| 2 | Slot spent before budget check | low | rejected | Only drifts the counter up by a slot; conservative; fix adds branches. |
| 3 | Second caller skips the wait in a moved window | medium | patch | Read `_reserve_slot`: after a move, `now < minute_start` and count 1 gave wait 0. Fixed; test added. |
| 4 | `JobBudget` default is new per call | medium | defer | Caller does not exist until 3.3; 3.3 must pass one shared budget. |
| 5 | `_log_call` raising in `finally` | low | rejected | Narrow SQLite-lock case; no misleading result stored. |
| 6 | `"your" in key` too broad | medium | patch | Replaced by a prefix rule; test with "your" inside a key. |
| 7 | No test with copied .env.example / hostile env | medium | patch | `StartWithoutKeyTests` runs settings in a child process. |
| 8 | No deliberately broken replay samples | medium | defer | Validators are story 3.3; broken samples belong with them. |
| 9 | `__cause__` assertion proves nothing | medium | patch | `from None` makes it always None; now asserts None and checks `assertLogs`. |
| 10 | Rate-row test weak | low | rejected | Behaviour covered by the new window test and `wait_over` test. |
| 11 | Spike bypasses ai_client | false | rejected | One-off in exempt `evaluation/`, plan marks it as a throwaway. |
| 12 | Task checkboxes not ticked | false | rejected | Bookkeeping; the work is in the diff. |
| 13 | `transport` bypasses the key check | low | rejected | Test-only parameter, documented. |
| 14 | Replay file names can collide (`a/b`, `a_b`) | maybe-false | rejected | Ids are integers or fixed names; would need a hostile id no caller makes. |

Full suite after patches: 131 tests OK; `makemigrations --check` reports no changes.

## Design Notes

The spike is done (see `docs/ai-model-choice.md`). Model ids came from the SDK's model list on the user's own key. Tests inject a fake transport raising 503 and 429; no real call, no key.

## Verification

**Commands:**
- `.venv/Scripts/python manage.py test` -- expected: all pass, no network
- `.venv/Scripts/python manage.py makemigrations --check` -- expected: no changes

**Manual checks (if no CLI):**
- The user creates `.env` with the key; the spike output shows only status and counts, never the key.
