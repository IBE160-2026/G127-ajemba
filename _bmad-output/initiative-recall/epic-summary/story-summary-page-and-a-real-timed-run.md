---
id: 4
type: story
title: "Summary page and a real timed run"
parent: epic-summary
covers: [FR-8, FR-9, FR-11, SM-1, SM-2]
after: [3]
refined: true
hitl: true
risk: medium
---

# Summary page and a real timed run

## Description

The student reads the Summary: short parts, each with its slides, and a list of key terms with simple explanations, under a notice that the content is AI-generated. The page shows AI text as plain text only. **Your part (hitl):** run a real upload of test lecture 1 with your real key and time it; the result is recorded.

## Acceptance Criteria

1. **Parts show their sources**
   **Given** a ready lecture
   **When** its owner opens the Summary page
   **Then** every Summary Part shows its heading, text and a Source Reference such as "Slides 12 to 15" (ranges only for three or more consecutive slides, otherwise "Slides 3, 7 and 12")
2. **Key terms are listed**
   **Given** the same page
   **When** it loads
   **Then** every Key Term is listed with its explanation
3. **The AI notice is always there**
   **Given** the Summary page
   **When** it loads
   **Then** the shared base template shows the notice that the content is AI-generated and should be checked against the slides
4. **AI text cannot become markup**
   **Given** a Summary Part whose text contains `<script>`
   **When** the page is rendered
   **Then** it is shown as escaped text, and a test finds no `|safe`, `mark_safe` or markdown-to-HTML on AI fields in any template
5. **Only the owner sees it**
   **Given** a lecture of user A
   **When** user B or a logged-out visitor requests its Summary
   **Then** the response is the shared 404 or the login redirect, with no data
6. **A real run is timed**
   **Given** your real key and test lecture 1
   **When** you upload it and wait for Ready
   **Then** `docs/summary-timing.md` records the elapsed time, model and prompt version; a text PDF of up to 30 pages takes under 60 seconds, and if not, the miss is recorded as a finding and not hidden
7. **Every real part has valid slides**
   **Given** the real Summary
   **When** the automatic check runs on it
   **Then** every Source Reference slide exists in the PDF (SM-2)
8. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** the "What we checked and what we did not" section is extended with the real Summary timing result and the plain statement that PDFs of 31 to 50 pages were not timed

## Tests

- `test_readme_has_required_sections` (the list already holds "What we checked and what we did not")
- `test_fr8_every_part_shows_source_reference`
- `test_fr9_key_terms_with_explanations_shown`
- `test_fr11_ai_notice_on_summary_page`
- `test_ad5_ai_text_is_escaped`, `test_ad5_no_safe_filter_in_templates`
- `test_summary_page_owner_only`
- `test_format_slides_runs_and_lists`
- Manual by you: timed real run (SM-1)

## Boundaries

- Must not change: the stored Summary rows and the validators. No quiz tab yet; the quiz link is added in epic-multiple-choice-results.

## References

- parent — _bmad-output/initiative-recall/epic-summary/epic-summary.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-5.4, AD-16.5, AD-19, AD-21.2, AD-22
- design — _bmad-output/initiative-recall/ux-recall/wireframes/05-summary.md; DESIGN.md
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-8, FR-9, FR-11, SM-1, SM-2

## Notes

- The timing depends on Gemini free-tier rate limits on the day; note the model and date in the record.
