---
id: 1
type: story
title: "Freeze the Test Set"
parent: epic-evaluation
covers: [FR-26]
after: [2.1]
refined: true
hitl: true
risk: medium
---

# Freeze the Test Set

## Description

**This is mostly your work, not code.** The Test Set is two lectures: your own deck from epic 2, and one freely licensed deck of 10-12 slides (for example from OpenStax), with the licence checked and credited. You write the Reference Key Points before any AI output is looked at, and you define what "unsupported statement" means. Then the files are frozen so they cannot be bent to fit the AI. You commit the frozen files yourself.

## Acceptance Criteria

1. **The licensed deck is clean**
   **Given** a freely licensed text-based deck exported to PDF
   **When** it is added to `evaluation/testset/`
   **Then** a licence file records the source link, licence name, date checked and the credit text, and no lecturer material is used
2. **Key points are written first**
   **Given** each of the two lectures
   **When** you write the Reference Key Points
   **Then** each lecture has at least five, each with its slide numbers, and they are committed before any AI output for that lecture is evaluated
3. **"Unsupported statement" is defined**
   **Given** PRD open question 6
   **When** you decide
   **Then** a file in `evaluation/testset/` defines unsupported statement (what counts as paraphrase, inference and omission) and states what happens if the target of no unsupported statement cannot be met, and the open question is marked closed in the initiative Notes
4. **Frozen files cannot change quietly**
   **Given** the Test Set files and their stored fingerprint (text with `\r\n` turned into `\n`)
   **When** any frozen file is changed
   **Then** a test fails with a message naming the file
5. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a "Test Set" section says what the two test lectures are, credits the licensed deck with its licence, and says the files are frozen

## Tests

- `test_readme_has_required_sections` (adds "Test Set" to the list)
- `test_fr26_frozen_files_match_fingerprint`
- `test_fr26_licence_file_exists_for_licensed_deck`
- `test_fr26_each_lecture_has_at_least_five_key_points_with_slides`

## Boundaries

- Must not change: app code. No copyrighted lecturer material, ever.

## References

- parent — _bmad-output/initiative-recall/epic-evaluation/epic-evaluation.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-6 (fingerprints), AD-13.5
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-26, open question 6

## Notes

- Decision: two test lectures, not three, to reduce human work (user, 2026-10-18).
- Decision: test lecture 1 is the builder's own deck; lecture 2 is freely licensed (user, 2026-10-18).
