---
id: 3
type: story
title: "Finish, compare, prompt fingerprints and the real run"
parent: epic-evaluation
covers: [FR-28, FR-30, SM-10, SM-11]
after: [2]
refined: true
hitl: true
risk: medium
---

# Finish, compare, prompt fingerprints and the real run

## Description

The second step of the evaluation: `evaluate --finish` refuses until every box on your review sheet is ticked, then prints pass or fail against the PRD targets. `--compare` shows what changed between two reports, and a fingerprint rule stops a prompt change that has no new version number. **Your part (hitl):** run the real evaluation with your key, fill in the review sheet, run finish, and keep the report. Any failure is recorded as a finding, not hidden.

## Acceptance Criteria

1. **Finish needs every box ticked**
   **Given** a report with one unticked box
   **When** `evaluate --finish <report>` runs
   **Then** it refuses and names the unticked box
2. **Finish judges the targets**
   **Given** a fully ticked report
   **When** `--finish` runs
   **Then** it prints pass or fail for each SM-10 target: at least 80% of Reference Key Points covered per lecture, no unsupported statement in any Summary, at least 90% of questions grounded and 100% with exactly one correct answer, 100% of answer keys correct, 100% of source references valid and at least 90% pointing to the right slides
3. **Compare shows differences**
   **Given** two reports
   **When** `evaluate --compare <a> <b>` runs
   **Then** it shows what changed per check, including Summary length next to coverage
4. **Prompt changes need a version**
   **Given** `evaluation/prompt_fingerprints.json` and prompt files
   **When** a prompt's text changed but its version did not
   **Then** `evaluate` refuses to run, and fingerprints are computed after turning `\r\n` into `\n`
5. **Changes are traceable**
   **Given** a prompt changelog line
   **When** a prompt changes
   **Then** the line names the evaluation report it was checked with, and reports from before and after are kept (SM-11)
6. **A real report is stored**
   **Given** your real key and the frozen Test Set
   **When** you run the evaluation and finish it
   **Then** a report is stored in `evaluation/reports/`, findings (including misses of the targets) are listed in it, and the README "what we checked" section is updated to match
7. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** the "What we checked and what we did not" section is extended with the real evaluation result, its findings and the limits from PRD §5.7 (one builder as judge, two test lectures, the fifteen-minute claim not measured)

## Tests

- `test_readme_has_required_sections` (the list already holds "What we checked and what we did not")
- `test_fr28_finish_refuses_with_unticked_box`
- `test_sm10_finish_prints_pass_or_fail_per_target` (fixture reports)
- `test_fr30_compare_shows_changed_checks`
- `test_ad6_changed_prompt_without_new_version_stops_run`
- `test_fingerprint_ignores_line_endings`
- Manual by you: the real run and the ticked review sheet

## Boundaries

- Must not change: the report format from story 2 beyond what compare and finish need.

## References

- parent — _bmad-output/initiative-recall/epic-evaluation/epic-evaluation.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-6, AD-13.2–13.4, AD-13.7
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-28, FR-30, SM-10, SM-11

## Notes

- The builder is the judge (PRD §5.7); a second AI as judge is rejected (AD-13.7).
- If a target is missed, the Decision from story 1 about unsupported statements says what happens next.
