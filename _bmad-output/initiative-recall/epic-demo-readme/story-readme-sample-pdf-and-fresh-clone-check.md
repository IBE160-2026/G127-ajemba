---
id: 2
type: story
title: "README, sample PDF and fresh-clone check"
parent: epic-demo-readme
covers: [FR-24, SM-9]
after: [1, 1.1]
refined: true
hitl: false
risk: medium
---

# README, sample PDF and fresh-clone check

## Description

The README already exists: it was started in epic 1 story 1 and every story since has added its own section. This story is the final check and polish. It adds `.env.example`, a small sample PDF and a fresh-clone script, then follows the README step by step from a fresh clone, fixes whatever does not work, and makes sure nothing is stale or missing. The README must never be at risk, so none of its content is written for the first time here.

## Acceptance Criteria

1. **Every setting is listed**
   **Given** `.env.example`
   **When** it is compared with the settings in `settings.py`
   **Then** every setting appears with a comment, `GEMINI_API_KEY=` is empty, and a test starts the app with a copy of it and with a hostile environment variable (a placeholder key) and both run in Demo Mode
2. **Secrets stay out of Git**
   **Given** the repository
   **When** the test scans tracked files
   **Then** `.env` is not tracked and no key-like string is in committed files (the test skips with a message when git is missing and then scans the files)
3. **A sample PDF is included**
   **Given** `samples/test.pdf`
   **When** it is opened
   **Then** it is small, made from your own or freely licensed slides, and contains no lecturer material
4. **The fresh-clone script proves the README**
   **Given** `scripts/fresh_clone_check.ps1`
   **When** it runs
   **Then** it builds a new virtual environment, installs the requirements, starts `run.py`, opens `/` and the demo, posts an example answer, tries an upload with no key and sees the needs-a-key message, and the result is written to `docs/fresh-clone-result.md`
5. **The README is followed from a fresh clone**
   **Given** a second folder with a fresh clone
   **When** you follow the README step by step without help
   **Then** every command works as written, and each step that failed is fixed in the README or the script, not worked around
6. **Nothing is missing or stale**
   **Given** the README
   **When** it is read from top to bottom
   **Then** it holds every section the earlier stories added (Install and start, Accounts, Privacy rules, Upload limits, AI notice and daily limit, Using your own Gemini key, How processing works, If you deploy this, Prompts, Quizzes, Results and saved lectures, Demo Mode, What we checked and what we did not, plus Test Set, Evaluation and the later ones for every story that was built), no section describes something that was dropped from the cut, and the statement of what was not checked matches the final state
7. **The checks hold**
   **Given** the README test
   **When** the suite runs
   **Then** `test_readme_has_required_sections` passes, and the list matches exactly the stories that were built

## Tests

- `test_fr24_env_example_lists_every_setting`
- `test_fr24_env_example_starts_in_demo_mode`
- `test_ad12_env_not_tracked_and_no_key_like_strings`
- `test_readme_has_required_sections` (list trimmed to what was built)
- Script check: `fresh_clone_check.ps1` passes and its result is stored
- Manual by you: follow the README once from a second folder

## Boundaries

- Must not change: app behaviour. If a README step fails, fix the README or the script, not unrelated code.

## References

- parent — _bmad-output/initiative-recall/epic-demo-readme/epic-demo-readme.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-12, AD-15.3–15.4, AD-16
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-24, SM-9, §5.7

## Notes

- Decision: the README is started in epic 1 story 1 and extended by every story, so it is never the part at risk; this story is only the final check and polish (user, 2026-10-18).
- If time is short, steps 5 and 6 are the part to do first, because they are what the examiner experiences.
