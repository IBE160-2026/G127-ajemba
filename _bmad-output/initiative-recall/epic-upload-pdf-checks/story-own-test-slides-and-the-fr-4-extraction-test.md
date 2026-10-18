---
id: 1
type: story
title: "Own test slides and the FR-4 extraction test"
parent: epic-upload-pdf-checks
covers: [FR-4]
after: [1.1]
refined: true
hitl: true
risk: medium
---

# Own test slides and the FR-4 extraction test

## Description

**Your part (hitl):** make test lecture 1, a 10-12 slide deck on a topic you know well (likely nursing), in PowerPoint, and export it to PDF with File, Save As, PDF. Use real slide habits: bullets, one slide with a table or diagram, one slide with long speaking-note text, and some words with "fi" or "fl". Then the agent builds `pdf_text.extract_pages` and `normalize_text`, runs both pdfplumber and pypdf on your PDF, and records the result. This is build step 2: the app must not move on to the Summary until the text is known to be usable.

## Acceptance Criteria

1. **Test lecture 1 exists**
   **Given** your PowerPoint deck
   **When** it is exported to PDF
   **Then** a PDF of 10 to 12 pages is saved in `evaluation/testset/` and a short note states it is your own work
2. **One string per page, always**
   **Given** `extract_pages(pdf)`
   **When** it reads a PDF with an image-only page in the middle
   **Then** it returns exactly one string per page in order, an empty string for the image page, and never skips a page, so index plus one is the slide number
3. **Text is cleaned in one place**
   **Given** extracted text with ligature glyphs, soft hyphens, a word split by a hyphen at a line break and extra spaces
   **When** `normalize_text` is applied
   **Then** the result is NFKC, case-folded, single-spaced, with the soft hyphens removed and the split word joined
4. **Both libraries are compared on your file**
   **Given** your PDF and 5 slides you pick
   **When** pdfplumber and pypdf both extract them
   **Then** `docs/extraction-test.md` records, per library, broken words (hyphenated line breaks, run-together words, ligature glyphs), the average characters per page, and which library is kept and why
5. **The threshold is checked against real slides**
   **Given** the average characters per page of your PDF
   **When** it is compared with the FR-4 threshold of 100
   **Then** `docs/extraction-test.md` states whether 100 still looks right, and if not, the proposed value is recorded as a Decision in this epic's Notes for you to confirm
6. **The README gets its part**
   **Given** the README
   **When** this story is done
   **Then** it starts a "What we checked and what we did not" section with the extraction test result and a link to `docs/extraction-test.md`, and a short "PDF requirements" line (text-based PDF only)

## Tests

- `test_readme_has_required_sections` (adds "What we checked and what we did not" to the list)
- `test_fr4_extract_pages_one_string_per_page` (small fixture PDFs: one with text, one with a blank page)
- `test_fr4_extract_pages_keeps_empty_page`
- `test_normalize_text_ligatures_hyphens_whitespace`
- Manual by you: the real-file comparison in `docs/extraction-test.md`

## Boundaries

- Must not change: nothing outside `pdf_text.py`, `text_utils.py`, the fixtures, `docs/` and the test lecture file. No upload page yet. Only `pdf_text.py` imports the PDF library. No copyrighted lecturer material.

## References

- parent — _bmad-output/initiative-recall/epic-upload-pdf-checks/epic-upload-pdf-checks.md
- architecture — _bmad-output/initiative-recall/architecture-recall/architecture-recall.md, AD-9, AD-21
- PRD — _bmad-output/initiative-recall/prd-recall/prd-recall.md, FR-4, open question 4

## Notes

- Decision: pdfplumber is the default; pypdf is kept only if it has fewer broken words in the 5-slide sample (AD-9). PyMuPDF is excluded (AGPL).
- Test lecture 1 is also used for the evaluation (epic-evaluation) and for the Example Lecture (epic-demo-readme), so choose a deck you are happy to keep.
