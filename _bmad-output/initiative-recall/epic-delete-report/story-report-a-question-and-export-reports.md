---
id: 2
type: story
title: "Report a question and export reports"
parent: epic-delete-report
covers: [FR-22, FR-31]
after: [4.2]
refined: true
hitl: false
risk: low
---

# Report a question and export reports

## Description

A student can report a question that looks wrong or unclear, with a short reason. The report stores a snapshot of the question so it stays useful even if the question is later deleted. There is no admin screen; the builder runs one command to export all reports to a file and reviews them by hand.

## Acceptance Criteria

1. **A report is stored with context**
   **Given** a question in a quiz
   **When** the student submits Report this question with a reason of at most `REPORT_MAX_CHARS` (300)
   **Then** a Report row stores the question, lecture, user, reason, timestamp, and a snapshot of the question text, key, Source References, prompt version and model
2. **The student sees a confirmation**
   **Given** a submitted report
   **When** it is saved
   **Then** a plain confirmation is shown and the quiz screen keeps its place
3. **The reason is bounded**
   **Given** a reason over 300 characters or empty
   **When** it is submitted
   **Then** it is refused with a plain message
4. **Only valid places report**
   **Given** another user's question, a logged-out visitor, or a GET request
   **When** a report is attempted
   **Then** it is refused (the shared 404 or login redirect), and reports on the Example Lecture are stored with no user
5. **The builder can export**
   **Given** stored reports
   **When** `manage.py export_reports` runs
   **Then** a file lists every report with all its fields
6. **A report survives its question**
   **Given** a report
   **When** its question is deleted with the lecture
   **Then** the report keeps its snapshot and the question link is empty
7. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Reporting a question" section says how students report, how the builder runs `manage.py export_reports`, and how to add a regression case to the Test Set

## Tests

- `test_readme_has_required_sections` (adds "Reporting a question" to the list)
- `test_fr22_report_stores_snapshot_and_reason`
- `test_fr22_reason_length_limit`
- `test_fr22_report_other_users_question_refused`
- `test_fr31_export_reports_lists_all_reports`
- `test_report_survives_question_deletion`

## Boundaries

- Must not change: quiz and scoring behaviour. No admin screen (PRD §8.2).

## References

- parent — _bmad-output/initiative-recall/epic-delete-report/epic-delete-report.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-13.8, AD-17 (Report row), AD-18.2
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-22, FR-31

## Notes

- FR-31 (reviewing reports and adding regression cases to the Test Set) is manual by design; the README gets one line saying how.
