---
title: 'Summary generation with validation and retries'
type: 'feature'
ticket: '3'
created: '2026-11-25'
status: 'built'
baseline_revision: 'e3fe681644b516f52e1cbe382a1ebf7f09a82bb7'
route: 'full'
route_source: 'auto'
risk: 'high'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: ['{project-root}/_bmad-output/initiative-recall/architecture-recall/architecture-recall.md', '{project-root}/_bmad-output/initiative-recall/epic-summary/story-summary-generation-with-validation-and-retries.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The Summary job is a stub that ends every lecture as Failed. Nothing builds a prompt, checks an AI answer, or stores a Summary, and a late or redelivered job could overwrite a retried lecture.

**Approach:** The job claims its lecture, asks `ai_client` for one Summary (versioned prompt, slide text as data, pure validators inside a retry loop of at most two retries, one shared time budget), and stores a good answer once in one short transaction. A bad answer fails the lecture cleanly with nothing stored.

## Boundaries & Constraints

**Always:** Carry-overs (user, 2026-11-25), each checked by a test:
1. **Claim step.** `Lecture.claimed_by` is set by one conditional UPDATE (`processing` and empty). Every status change, retry and reap clears it. The final write and the failure write both require the job's own token. A second, old or redelivered job cannot claim and stops.
2. **One shared budget.** The job makes one `JobBudget` and passes it to every `ai_client.call`, retries included. `AI_JOB_BUDGET_S` (220) stays below the worker timeout (240).
3. **Slide text is data.** Each page is wrapped in markers with a per-call random token, `<<` and `>>` are neutralised, and the prompt says marked text is data. Proof: a slide with instruction-like text and forged markers stays inside its markers, and a reply that follows it is rejected.
4. **No content in logs.** No slide text in queue tables, logs or error messages. Validation errors carry a reason code and a part number only. One `AiCallLog` row per real request, none in replay.
5. **Real slide numbers.** Every part cites at least one slide, all within 1 to the page count.

Output is stored as plain text. Only `ai_client.py` loads `prompts/summary.md`. Tests use replay or a fake transport: no key, no network. Python is `.venv/Scripts/python`. No new package. Never read `.env`.

**Never:** No real Gemini call before the user hears the call count and says yes; only `evaluation/testset/test-lecture-1.pdf`, on a throwaway database. No quiz generation, no Summary page (story 3.5), no change to upload checks, messages or the status rules. No commit.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Good answer | valid JSON, all checks pass | parts, key terms, `language`, `generated_with`, `ready`, one transaction | none |
| Broken answer | wrong shape, slide out of range or none, term not in text, empty explanation, language not `en`/`nb`, `http` `<` `>` `hx-` | rejected, retried, at most 2 retries | after the last: `failed`, FR-5 message, no rows |
| Old or redelivered job | claim already taken, or status not `processing` | stops before any AI call | none |
| Lecture deleted or retried during the call | row gone, or token no longer matches | output dropped silently | none |
| Text over `MAX_PROMPT_CHARS` | long lecture | refused with the "too much text" message, no call | `failed` |
| Time used up | budget empty | `failed` with FR-5 message | `AiCallFailed` |
| Replay, no sample | no stored file | `failed` calmly | `AiReplayMissing` |

</frozen-after-approval>

## Code Map

- `core/ai_client.py` -- keep `call()`, `_attempt()` (one `AiCallLog` row per request), `JobBudget`. Add `build_summary_prompt(pages)` (loads the prompt, neutralises, wraps) and `generate_summary(user, lecture_id, pages, budget, transport=None)` with the validation retry loop. Replay mode validates once, no retry.
- `core/validation.py` (new, pure) -- `validate_summary(output, page_texts)` returns a checked structure or raises `ValidationFailed(reason)`; uses `text_utils.normalize_text`.
- `core/types.py` (new, pure) -- frozen `SourceRef` (sorted, de-duplicated slide numbers, range-checked). Other dataclasses are story 4.1.
- `prompts/summary.md` (new) -- header with `version` and a changelog line, plain-language body, slots `{{PAGES}}`.
- `lectures/models.py` + `0006` -- `Lecture.claimed_by`; `SummaryPart` (lecture, order, heading, text, source_refs JSON) and `KeyTerm` (part, term, explanation); owner-scoped `for_user`.
- `lectures/services.py` -- `claim_lecture`, claim-checked `fail_claimed` and `store_summary`; `set_status`, `reap_stale`, `retry_lecture` clear `claimed_by`; `run_summary(lecture_id)` is the job body.
- `core/jobs.py` -- `summary_job` calls `services.run_summary`; `run_job` and its class-name-only error stay.
- `core/sample_responses/summary__sample-1.json` -- becomes the valid shape (key terms inside parts); new `summary__broken-*.json` files.
- `core/tests.py` -- pure-module and import rules already cover `validation` and `types`.
- `lectures/test_processing.py` -- stub-based tests change (the job now needs a sample to reach `ready`); `RealWorkerTests` still ends `failed` (no pages, no key).
- `README.md`, `docs/required_readme_headings.txt` -- add "Prompts".

## Tasks & Acceptance

**Execution:**
- [ ] `lectures/models.py` + migration -- `claimed_by`, `SummaryPart`, `KeyTerm` -- AC 3
- [ ] `core/types.py`, `core/validation.py` -- `SourceRef` and the checks -- AC 4
- [ ] `prompts/summary.md` -- version 1, plain language, language of the slides, marked text is data -- AC 1
- [ ] `core/ai_client.py` -- prompt builder, protection, retry loop, shared budget -- AC 2, 5
- [ ] `lectures/services.py`, `core/jobs.py` -- claim, final write, drop rules, job body -- AC 3, 6, 7
- [ ] `core/sample_responses/` -- valid and broken samples (wrong shape, slide 99, slide 0, term not in text, empty explanation, language `fr`, `http`, `<b>`, `hx-`)
- [ ] `core/test_validation.py`, `core/test_summary_job.py`, `lectures/test_processing.py` -- the story's seven tests, plus claim, budget, injection, no slide text in logs, the stored failed-job string and the queue rows (an exception raised with slide text), one log row per request, `SummaryPart.source_refs` all within range
- [ ] `README.md`, headings file -- "Prompts" section -- AC 8

**Acceptance Criteria:**
- Given the full suite, when `.venv/Scripts/python manage.py test` runs with no `.env`, then all tests pass and `makemigrations --check` reports no changes.
- Given an old job queued before a retry, when both run, then only one calls the AI and the lecture ends with one Summary.
- Given three broken answers in a row, when the job runs, then three `AiCallLog` rows exist, the lecture is `failed` and no `SummaryPart` exists.

## Implementation Notes

## Plan Change Log

## Review Triage Log

Pass 1, 2026-11-25. Quick lens (reviewer subagent). 7 findings: 1 medium (patched by the user's decision), 3 low patched, 1 low deferred, 2 false. No intent_gap or bad_plan, so no loop-back.

| # | Finding | Verdict | Route | Evidence / action |
|---|---------|---------|-------|-------------------|
| 1 | "Too much text" message never reaches the student; Try again can never work for that PDF | low | defer | `Lecture` has no message field and the Failed page shows the generic text; a fix adds a field or UI (story 3.5 or polish). Entry in `deferred-work.md` |
| 2 | The forbidden-text check also rejects a grounded key term such as "HTTP", and any text naming the protocol | medium | patch (user decision, 2026-11-25) | Real. The user decided: block real links (`http://`, `https://`, `www.`) and angle brackets, keep `hx-` blocked, allow the plain word "HTTP". `FORBIDDEN_FRAGMENTS` changed, prompt rule and README updated; tests: term "HTTP" in the slides is accepted, `https://example.com` is rejected in heading, text and explanation. This narrows AD-5.4 and AC 4 by the owner's choice; the frozen block is unchanged. The deferred-work entry was removed |
| 3 | Lecture deleted between the claim and the page read raised and stored a failed task | low | patch (done) | `run_summary` now reads with `filter().first()` and returns; new test |
| 4 | Prompt header says version 2, plan task says version 1 | n/a | rejected (false) | The user asked for the bump on 2026-11-25; v1 was never used, and the changelog says so |
| 5 | Validator limits (30 parts, 12 terms, field lengths) were not in the prompt | low | patch (done) | Limits added to the prompt rules; changelog line updated; version stays 2 (not yet used) |
| 6 | Every retry sends the same prompt (new token only) | n/a | rejected (false) | The plan allows it; AD-4.4 only bounds the number of attempts. No hint is sent on purpose, so no model text is echoed back |
| 7 | Part number dropped from the failure reason in logs | low | patch (done) | Reason is now `invalid:<code> (part n)`; test checks it and that no slide text is logged |

## Design Notes

- `claimed_by` was chosen over a counter because the job gets only an id (AD-3.1), so it cannot carry a generation. A job that dies after claiming leaves the lecture `processing` until the 10-minute reaper, and a redelivered task cannot take it.
- Replay id is the lecture id, so a real upload without a key fails calmly unless a stored sample exists. Tests point `SAMPLE_DIR` at a temporary folder.
- A real model's obedience to injected slide text can only be seen in a real run; automated tests prove the framing and that a disobedient reply is rejected. The real call uses only the user's lecture.
- Valid shape: `{"language", "parts": [{"heading", "text", "slides", "key_terms": [{"term", "explanation"}]}]}`.

- Suggested text for the story's AC 4, for the owner to paste (not applied to the story file): "**Given** a response with a wrong structure, a slide number outside the PDF, a part with no slide number, a key term not in the lecture text, a missing explanation, a language code other than `en` or `nb`, or text containing a real link (`http://`, `https://`, `www.`), `<`, `>` or `hx-` **When** it is validated **Then** it is rejected and nothing is stored. The plain word HTTP is allowed (decision 2026-11-25)."

## Verification

**Commands:**
- `.venv/Scripts/python manage.py test` -- expected: all pass, no network
- `.venv/Scripts/python manage.py makemigrations --check` -- expected: no changes

**Manual checks (if no CLI):**
- After the user's yes: one real run on a throwaway database with test lecture 1; the whole Summary is shown to the user for a nurse's check.
