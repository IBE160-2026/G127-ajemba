---
title: 'Own test slides and the FR-4 extraction test'
type: 'feature'
ticket: 'story-own-test-slides-and-the-fr-4-extraction-test'
created: '2026-11-19'
status: 'in-review'
baseline_revision: '59b17eab5c020e1deb95c07076db51f5545707c0'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: []
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The app must not move on to the Summary until the text of a real PowerPoint-exported PDF is known to be usable (FR-4, AD-9). There is no `pdf_text.py`, no `text_utils.py`, no extraction result and no README section about it.

**Approach:** Add `core/pdf_text.extract_pages` (pdfplumber) and `core/text_utils.normalize_text`, compare pdfplumber and pypdf on the user's own deck (`evaluation/testset/test-lecture-1.pdf`, already copied with its own-work note), record the result in `docs/extraction-test.md`, and start the README section.

## Boundaries & Constraints

**Always:** Only `core/pdf_text.py` imports pdfplumber. `extract_pages` returns exactly one string per page, in order; an image-only page gives `""`; pages are never filtered. `normalize_text` lives only in `core/text_utils.py` and is pure (no models, request, network). pdfplumber is the default; pypdf wins only with fewer broken words in the 5-slide sample. `requirements.txt` gets `pdfplumber==0.11.10` and not pypdf (user decision). `evaluation/compare_pdf_libraries.py` starts with a comment: needs `pypdf==7.1.1` installed separately, not part of the app. `docs/extraction-test.md` refers to it. The import-boundary test fails when any app code (everything except `evaluation/`) imports pypdf.

**Never:** If pypdf wins, stop and ask the user before changing anything. No upload page, no changes outside `core/pdf_text.py`, `core/text_utils.py`, fixtures, tests, `docs/`, `evaluation/`, `requirements.txt`, README. Do not edit ticket or epic files. No commit. Stop any test server started.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Text PDF | 2 pages with text | list of 2 strings, in order | none |
| Image-only middle page | 3 pages, page 2 blank | 3 strings, index 1 is `""` | none |
| Page with no extractable text | `extract_text()` returns None | `""` | none |
| Ligatures/soft hyphens | `ﬁnal­ly`, `ﬂow` | `finally`, `flow` | none |
| Line-break hyphen | `exam-\nple` | `example` | none |
| Extra spaces | `a   b \n c` | `a b c` | none |

</frozen-after-approval>

## Code Map

- `core/tests.py` -- import-boundary test: `SINGLE_OWNER_RULES`, `PURE_FORBIDDEN_PREFIXES`, `project_python_files` (scans root `*.py` and packages with `__init__.py`). Add pypdf: no owner allowed, `evaluation/` exempt, pure modules forbid it, plus a temp-folder case.
- `core/` has only `__init__.py`, `tests.py`. Create `pdf_text.py`, `text_utils.py`. Tests for them go in `core/tests.py` or a new `core/test_pdf_text.py` (Django discovers `test*.py`), fixtures built in code as raw PDF bytes (no extra package).
- `config/tests.py:120` `test_readme_has_required_sections` reads `docs/required_readme_headings.txt` (add "What we checked and what we did not").
- `README.md` -- add section + "PDF requirements" line. Existing sections: Install and start, Accounts, Privacy rules.
- `requirements.txt` -- Django, django-environ only. Add `pdfplumber==0.11.10`.
- `.venv` has pdfplumber 0.11.10 and pypdf 7.1.1 installed.

## Tasks & Acceptance

**Execution:**
- [ ] `core/text_utils.py` -- `normalize_text`: NFKC, remove soft hyphens, join hyphen+line-break words, case-fold, collapse whitespace -- AC3
- [ ] `core/pdf_text.py` -- `extract_pages(pdf) -> list[str]` with pdfplumber, `None` becomes `""`; also an average-characters-per-page helper -- AC2, AD-9
- [ ] `core/test_pdf_text.py` -- the 3 named tests with generated fixture PDFs (text; blank middle page) -- AC2, AC3
- [ ] `core/tests.py` -- pypdf boundary rule and violation test -- user request
- [ ] `evaluation/compare_pdf_libraries.py` -- runs both libraries on `test-lecture-1.pdf` and 5 chosen pages; counts broken words, average chars per page -- AC4
- [ ] `docs/extraction-test.md` -- results, sample slides, kept library and why, 100-threshold verdict, proposed Decision text for the user to paste into the epic's Notes, reference to the script -- AC4, AC5
- [ ] `requirements.txt`, `docs/required_readme_headings.txt`, `README.md` -- as above -- AC6

**Acceptance Criteria:**
- Given the test deck, when `python manage.py test` runs, then all tests pass and the PDF in `evaluation/testset/` has 10 to 12 pages.
- Given a file in `core/` importing pypdf, when the boundary test runs, then it reports it; a file in `evaluation/` importing it is not reported.

## Implementation Notes

Built directly in the session (no subagent). Files: `core/text_utils.py`, `core/pdf_text.py`, `core/test_pdf_text.py`, `core/tests.py`, `evaluation/compare_pdf_libraries.py`, `evaluation/testset/` (PDF and note), `docs/extraction-test.md`, `docs/required_readme_headings.txt`, `README.md`, `requirements.txt`, `architecture-recall.md`, `initiative-recall.md`. Full test run: 46 tests OK. The 5-slide comparison gave 0 broken words in both libraries; pdfplumber mixed columns.

## Plan Change Log

- 2026-11-19, user decision after the comparison: library changed from pdfplumber to pypdf 7.1.1 because pdfplumber mixes columns on multi-column slides and word order changes meaning (hand rub vs. soap and water). This overrides the AD-9 broken-words rule (0 vs 0). Effect: `core/pdf_text.py` uses pypdf; `requirements.txt` has pypdf==7.1.1 and not pdfplumber; the boundary test is reversed (only `core/pdf_text.py` may import pypdf, no app code may import pdfplumber, `evaluation/` exempt); AD-9, AD-2.4, Stack and Deferred rows updated with a Change log entry. The frozen Intent and Boundaries above still say pdfplumber and are kept as approved; this entry supersedes them. KEEP: `normalize_text`, the fixtures and the evaluation script.

## Review Triage Log

Quick review done inline by the builder (no subagent was launched). Checked: AC1 to AC6 against the files and a green full run (46 tests); the import boundary both ways; README claims only describe what exists (scanned-PDF rejection marked as later). Open point: page header and footer text stays in the extracted text (low, recorded in docs).

## Design Notes

AC5 asks for a Decision in the epic's Notes; the build workflow may not write ticket files, so the proposed text goes in `docs/extraction-test.md` for the user to paste.

## Verification

**Commands:**
- `.venv/Scripts/python manage.py test` -- expected: all tests pass
- `.venv/Scripts/python evaluation/compare_pdf_libraries.py` -- expected: prints per-library counts
