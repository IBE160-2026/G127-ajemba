---
id: 2
type: story
title: "The evaluate command and report"
parent: epic-evaluation
covers: [FR-28]
after: [1, 3.3, 4.2]
refined: true
hitl: false
risk: medium
---

# The evaluate command and report

## Description

`python manage.py evaluate` runs each Test Set lecture through the same Summary and Multiple Choice code the app uses, applies the automatic checks, and writes a dated report to `evaluation/reports/` with a review sheet for you to fill in. It writes nothing to user tables, never runs inside `manage.py test`, and can resume after an interruption. This story is proved on replay data; the real run is story 3.

## Acceptance Criteria

1. **It uses the real code path without touching user data**
   **Given** the two test lectures
   **When** `evaluate` runs
   **Then** it extracts each PDF, generates the Summary and Multiple Choice questions through `ai_client`, keeps results in memory and in its own cache, and writes nothing to Lecture or Quiz tables
2. **Automatic checks run**
   **Given** the generated output
   **When** the checks run
   **Then** the report lists per lecture: structure valid, every slide reference exists, every key term appears in the text, every Multiple Choice question has exactly one correct option, and elapsed time per lecture (SM-1)
3. **The report is traceable**
   **Given** a finished run
   **When** the report file is read
   **Then** it carries the date, the model, each prompt's version and fingerprint, and the report name is printed
4. **A review sheet is written**
   **Given** the report
   **When** you open it
   **Then** it holds checkboxes for faithfulness, completeness against the Reference Key Points, question grounding, answer keys, source-reference spot check (at least 10 per lecture) and wording (FR-10), shown next to the slide text
5. **Counter-metrics are visible**
   **Given** the report
   **When** it is read
   **Then** it shows Summary length next to key-point coverage (SM-C3), a field for duplicate, wrong or unclear questions per lecture (SM-C1) and a difficulty note (SM-C2)
6. **An interrupted run resumes**
   **Given** results cached per (lecture, task, prompt fingerprint, run number)
   **When** `evaluate` is run again after an interruption
   **Then** finished calls are not repeated, and it paces itself to the rate limits
7. **It never runs in the test suite**
   **Given** `manage.py test`
   **When** the command is called from a test
   **Then** it refuses to run, and its own tests use replay data only
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** an "Evaluation" section says how to run `manage.py evaluate`, where reports are written and what the review sheet is

## Tests

- `test_readme_has_required_sections` (adds "Evaluation" to the list)
- `test_fr28_evaluate_writes_report_with_checks_on_replay_data`
- `test_fr28_report_records_prompt_versions_and_fingerprints`
- `test_fr28_evaluate_writes_nothing_to_user_tables`
- `test_fr28_cached_results_resume_run`
- `test_evaluate_refuses_inside_test_run`

## Boundaries

- Must not change: Summary and quiz generation code (call it, do not copy it). Fill-in and essay checks are added in later epics.

## References

- parent — _bmad-output/initiative-recall/epic-evaluation/epic-evaluation.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-6, AD-13, AD-14, AD-18.1
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-28, §5.4, SM-C1 to SM-C3

## Notes

- Daily Gemini limits may stretch a real run over several days; the cache makes that safe.
