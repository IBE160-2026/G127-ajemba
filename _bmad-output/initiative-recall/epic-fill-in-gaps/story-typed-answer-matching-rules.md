---
id: 1
type: story
title: "Typed-answer matching rules"
parent: epic-fill-in-gaps
covers: [FR-15, SM-4]
after: [4.1]
refined: true
hitl: false
risk: low
---

# Typed-answer matching rules

## Description

A pure module decides whether a typed answer matches the expected term, using fixed rules and no AI. It uses the shared text normalisation so ligatures and spacing never cause a false miss. This is the cheapest story in the plan and it proves SM-4 on its own.

## Acceptance Criteria

1. **Case and spaces are ignored**
   **Given** the expected answer "third normal form"
   **When** the typed answer is " Third  Normal Form "
   **Then** it is accepted
2. **One wrong letter is accepted for longer terms**
   **Given** an expected answer of 5 letters or more
   **When** the typed answer has an edit distance of one (one letter replaced, added or removed)
   **Then** it is accepted, so "normalisaton" is accepted for "Normalisation"
3. **Short terms need an exact match**
   **Given** an expected answer shorter than 5 letters
   **When** the typed answer differs by one letter
   **Then** it is rejected, so "kay" is rejected for "key"
4. **Anything else is wrong**
   **Given** an edit distance of two or more (a swap of two letters counts as two), or an empty answer
   **When** it is matched
   **Then** it is rejected
5. **The module is pure**
   **Given** `matching.py`
   **When** the import-boundary test runs
   **Then** it imports no models, no request and no network, and edit distance is computed on normalised text
6. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** a short "Fill-in answer rules" section lists the matching rules with the three examples

## Tests

- `test_readme_has_required_sections` (adds "Fill-in answer rules" to the list)
- `test_sm4_normalisation_accepts_one_wrong_letter`
- `test_sm4_key_vs_kay_rejected`
- `test_sm4_third_normal_form_with_odd_spacing_accepted`
- `test_fr15_length_boundary_five_letters`
- `test_fr15_two_edits_and_empty_rejected`

## Boundaries

- Must not change: `normalize_text` behaviour from epic 2. No questions or screens here.

## References

- parent — _bmad-output/initiative-recall/epic-fill-in-gaps/epic-fill-in-gaps.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-2.2, AD-21.1
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-15, SM-4

## Notes

- Tier: if-time. Can be done early in a short free evening because it needs no AI and no key.
