---
id: 3
type: story
title: "Essay screen with drafts and three submissions"
parent: epic-essay-feedback
covers: [FR-17, FR-18, FR-19]
after: [2, 4.3]
refined: true
hitl: false
risk: high
---

# Essay screen with drafts and three submissions

## Description

The student writes an essay answer, with the text saved as a draft while typing, and can ask for feedback up to 3 times per essay. All submissions and their feedback stay visible, and the last finished one counts for the rating and the Review List. The results page shows every submission's rating.

## Acceptance Criteria

1. **Drafts are saved**
   **Given** the essay screen
   **When** the student stops typing for `DRAFT_SAVE_MS` (2000 ms)
   **Then** the draft is saved on the server and its `version` goes up, the browser keeps a backup under a key with the user id, and the backup is used only if its version is not lower than the server's
2. **Backups never leak between users**
   **Given** a backup in the browser
   **When** the student submits, logs out, or a different user loads the page
   **Then** the backup is deleted
3. **A failed save keeps the text**
   **Given** a save that fails
   **When** the failure happens
   **Then** a plain message shows and the typed text stays
4. **Three submissions, then no more**
   **Given** an essay with 3 submissions
   **When** a fourth is posted
   **Then** it is refused, the page says all 3 have been used, and `seq` is assigned inside one IMMEDIATE transaction so two quick posts cannot make a fourth
5. **The draft ends with the submission**
   **Given** a submission
   **When** it is created
   **Then** the draft row is deleted in the same transaction
6. **All feedback stays visible, the last counts**
   **Given** two finished submissions
   **When** results open
   **Then** both are listed with their ratings (for example "Attempt 1: 1 of 3 points, Attempt 2: 3 of 3 points"), the last finished one sets the rating shown, and a failed submission does not use up one of the 3
7. **The Review List uses the last submission only**
   **Given** an essay whose last submission still misses a key point
   **When** the Review List is built
   **Then** there is one entry for its Summary Part with its Source Reference, and earlier submissions do not count
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** an "Essay drafts and submissions" section says that drafts are saved, up to 3 submissions are allowed and the last one counts

## Tests

- `test_readme_has_required_sections` (adds "Essay drafts and submissions" to the list)
- `test_fr17_fourth_submission_refused`
- `test_fr17_draft_deleted_in_same_transaction_as_submission`
- `test_fr18_results_list_every_submission_rating`
- `test_fr19_review_list_uses_last_submission_only`
- `test_failed_submission_does_not_count_toward_three`
- `test_draft_version_prevents_stale_overwrite`

## Boundaries

- Must not change: scoring for Multiple Choice and Fill-in; the rating function from story 2.

## References

- parent — _bmad-output/initiative-recall/epic-essay-feedback/epic-essay-feedback.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-11.3–11.4, AD-17, AD-18.4–18.6, AD-19.3
- design — _bmad-output/initiative-recall/ux-recall/wireframes/08-quiz-essay.md and 09-results.md; EXPERIENCE.md (Essay behaviour)
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-17 to FR-19

## Notes

- In code, "attempt" means `Attempt`; the student-facing "Attempt 2 of 3" is `EssaySubmission.seq` (AD-18.6).
