---
id: 1
type: story
title: "Delete a lecture"
parent: epic-delete-report
covers: [FR-21]
after: [4.3]
refined: true
hitl: false
risk: medium
---

# Delete a lecture

## Description

A student can delete one of their lectures, which removes its summary, questions, attempts and stored page text in one transaction. This is a privacy safeguard because lecture text goes to an external AI service. Deleting works in any state, including a lecture stuck in processing.

## Acceptance Criteria

1. **Everything is removed**
   **Given** a lecture with a Summary, a quiz, attempts and page text
   **When** its owner confirms deletion with a POST request
   **Then** all of it is deleted in one transaction, the lecture is gone from the list, and its address returns the shared 404
2. **Deleting needs a confirmation**
   **Given** the lecture page
   **When** the student presses Delete
   **Then** a confirmation asks first, and a GET request never deletes
3. **It works while processing**
   **Given** a lecture in `processing` or `making`
   **When** it is deleted
   **Then** it is removed, and a running job checks its row before its final write and silently drops the output
4. **Others and examples are protected**
   **Given** another user's lecture or the Example Lecture
   **When** a delete is posted
   **Then** the shared 404 is returned and nothing changes
5. **Reports keep their snapshot**
   **Given** a Report about one of its questions
   **When** the lecture is deleted
   **Then** the Report stays with its snapshot and its question link set to empty
6. **The daily limit is not reduced**
   **Given** an upload counted today
   **When** its lecture is deleted
   **Then** the count for the day does not go down
7. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Deleting a lecture" section says what deletion removes and that it cannot be undone

## Tests

- `test_readme_has_required_sections` (adds "Deleting a lecture" to the list)
- `test_fr21_delete_removes_all_rows_and_returns_404`
- `test_fr21_delete_requires_post_and_confirmation`
- `test_delete_during_processing_drops_job_output`
- `test_delete_other_users_and_example_lecture_refused`
- `test_report_snapshot_survives_lecture_delete`
- `test_delete_does_not_reduce_daily_upload_count`

## Boundaries

- Must not change: the upload limit counting rules; other users' data.

## References

- parent — _bmad-output/initiative-recall/epic-delete-report/epic-delete-report.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-3.8, AD-8.3, AD-15.5, AD-18.2
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-21

## Notes

- Tier: if-time, priority 3.
