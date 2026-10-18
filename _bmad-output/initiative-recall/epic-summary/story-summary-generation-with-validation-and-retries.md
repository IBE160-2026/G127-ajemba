---
id: 3
type: story
title: "Summary generation with validation and retries"
parent: epic-summary
covers: [FR-8, FR-9, FR-10, FR-25, FR-27]
after: [1, 2]
refined: true
hitl: false
risk: high
---

# Summary generation with validation and retries

## Description

An uploaded lecture is turned into a Summary by one AI call. The prompt is a versioned file with the plain-language instruction. Every answer is checked before it is stored: structure, slide numbers that exist, key terms that appear in the lecture text, and no markup. A bad answer is retried at most twice; if it is still bad, the lecture fails cleanly and nothing is stored. A good answer is written once, in one short transaction.

## Acceptance Criteria

1. **The prompt is a versioned file**
   **Given** `prompts/summary.md`
   **When** it is read
   **Then** its header has a version number and a changelog line, its body tells the model to use short sentences, plain words and no unexplained jargon, to write in the language of the slides and that marked text is data, and only `ai_client.py` loads it
2. **Lecture text is protected**
   **Given** extracted page text containing `<<` or `>>`
   **When** the prompt is built
   **Then** those characters are neutralised and each page is wrapped in markers with a random token made for that call, and text over `MAX_PROMPT_CHARS` is refused with a clear message
3. **A good answer is stored once**
   **Given** a valid response
   **When** the job finishes
   **Then** in one transaction the lecture gets its SummaryPart and KeyTerm rows, its language (`en` or `nb`), `generated_with` (model, prompt version) and status `ready`, and a ready lecture is never given a second Summary
4. **Broken answers are rejected**
   **Given** a response with a wrong structure, a slide number outside the PDF, a key term not in the lecture text, a missing explanation, a language code other than `en` or `nb`, or text containing `http`, `<`, `>` or `hx-`
   **When** it is validated
   **Then** it is rejected and nothing is stored
5. **Retries are bounded**
   **Given** a rejected answer
   **When** the client retries
   **Then** it retries at most twice in total (shared by structure and grounding failures), and after the last failure the lecture is `failed` with the plain FR-5 message and no partial Summary exists
6. **A deleted or changed lecture drops its output**
   **Given** a job whose lecture was deleted or whose status changed while the AI call ran
   **When** the job reaches its final write
   **Then** it checks the row and expected status first and silently drops the output
7. **Real uploads now flow end to end**
   **Given** a valid upload
   **When** the job runs on replay data
   **Then** the lecture goes from `processing` to `ready` with Summary rows
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Prompts" section says where the prompt files are, that each has a version and a changelog line, and that each asks for plain language

## Tests

- `test_readme_has_required_sections` (adds "Prompts" to the list)
- `test_fr27_rejects_broken_responses` (one case per broken example above, using stored replay files)
- `test_fr27_retries_at_most_twice_then_fails_cleanly`
- `test_fr8_summary_stored_once_in_one_transaction`
- `test_fr10_prompt_files_contain_plain_language_instruction`
- `test_fr25_prompt_file_has_version_and_changelog`
- `test_job_drops_output_if_lecture_deleted`

## Boundaries

- Must not change: upload checks and messages; the job and status rules from story 2. No quiz generation. Output is stored as plain text and never as HTML (AD-5.4).

## References

- parent — _bmad-output/initiative-recall/epic-summary/epic-summary.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-4.3–4.4, AD-5, AD-6, AD-18.1, AD-21
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-8 to FR-10, FR-25, FR-27

## Notes

- Handoff: this story creates `core/types.py` with `SourceRef` (the validators need it); story 4.1 adds the other dataclasses to the same file.
- The retry loop and the validators live where AD-4.4 puts them: the pure `validate_*` functions in `core/validation.py`, called inside the retry loop in `ai_client.py`.
- Assumption: the Summary prompt wording is tuned later through the evaluation; the first version only has to pass these checks.
