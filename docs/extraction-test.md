# FR-4 extraction test (story 2.1)

Run on 2026-11-19 on `evaluation/testset/test-lecture-1.pdf` (12 slides, hand hygiene; made with ChatGPT help and checked by the author, see `evaluation/testset/test-lecture-1-NOTE.md`).
Libraries: pdfplumber 0.11.10 and pypdf 7.1.1. The comparison can be repeated with `evaluation/compare_pdf_libraries.py`. It needs both `pypdf==7.1.1` (in `requirements.txt`) and `pdfplumber==0.11.10` (installed separately, not part of the app).

## Sample: 5 slides chosen by the builder

Slides 3, 5, 6, 8 and 10. They have the hardest layouts: three or two columns (3, 5, 8, 10) and numbered steps (6).

## Result

| | pdfplumber | pypdf |
|---|---|---|
| Hyphenated line breaks (5-slide sample) | 0 | 0 |
| Run-together words | 0 | 0 |
| Ligature glyphs | 0 | 0 |
| Replacement characters | 0 | 0 |
| Average characters per page (all 12 pages) | 334.3 | 337.9 |
| Shortest page (characters) | 138 | 141 |

The counts are 0 for all 12 pages in both libraries. The script counts with regular expressions; the 5 slides were also read side by side by eye.

What differs is reading order, not broken words:

- **pdfplumber** reads line by line across the page. On slides with two or three columns, lines of neighbouring columns are mixed. On slide 5 it gives "Preferred for most routine healthcare Use when hands are visibly dirty or", which puts the hand rub text and the soap and water text in one line.
- **pypdf** keeps each column together: "ALCOHOL-BASED HAND RUB / Preferred for most routine healthcare situations ..." and then "SOAP + RUNNING WATER / Use when hands are visibly dirty ...". It also keeps the numbers with their steps on slide 6. It adds some double spaces and stray leading spaces (28 and 3 in this deck) and puts the page header and footer ("HAND HYGIENE · INFECTION PREVENTION", "03 / 12") right after the title.

`normalize_text` removes the extra spaces and line breaks (0 double spaces and 0 newlines left on all 12 pages). It does not remove the header and footer text.

## Decision (changed by the user on 2026-11-19)

**pypdf 7.1.1 is used** in `core/pdf_text.py` and is in `requirements.txt`. pdfplumber is not part of the app and no app code may import it (the import-boundary test in `core/tests.py` checks this; `evaluation/` is exempt).

My first recommendation was pdfplumber. AD-9 says pypdf is kept only if it has fewer broken words, and both had 0, so by that rule pdfplumber stayed the default. The user changed the decision and overrode the rule: **word order matters for meaning, not only broken words.** When pdfplumber mixes the columns, hand rub and soap and water advice end up in the same sentence, and the Summary can then state something wrong. pypdf keeps the columns apart.

pypdf's licence is BSD-3-Clause (checked on PyPI, 2026-11-19). The change is recorded in the architecture's Change log.

Known limit: the header and footer text of each slide is part of the page text. It is not filtered. Check whether it disturbs the Summary in the Summary epic.

## Is the FR-4 threshold of 100 characters per page still right?

The average is 338 characters per page with pypdf, and the shortest page (the title slide) has 141. All pages are above 100, so **100 still looks right for this deck**. One text-rich deck is a thin basis: image-heavy slides with little text could fall below 100 and be taken for scanned. No change is proposed now. Check again with test lecture 2 (a freely licensed deck).

## Suggested texts for the planning files (paste them in yourself)

The build workflow does not edit epic or story files. These are the texts to paste.

**`epic-upload-pdf-checks.md`, Notes** (add):

> - Decision (2026-11-19, user): the extraction library is pypdf 7.1.1, not pdfplumber 0.11.10. Both had 0 broken words on test lecture 1, but pdfplumber mixes columns on multi-column slides, which changes meaning (hand rub vs. soap and water). See `docs/extraction-test.md`.
> - Decision: keep the FR-4 threshold at 100 characters per page. Test lecture 1 averages 338 (shortest page 141). Recheck with test lecture 2.

**`epic-upload-pdf-checks.md`, Boundaries**: replace "Only `pdf_text.py` imports pdfplumber." with "Only `pdf_text.py` imports pypdf."

**`epic-upload-pdf-checks.md`, Unknown** (line "whether pdfplumber output is clean enough or pypdf is better"): mark as settled, "settled: pypdf, see Decision above."

**`story-own-test-slides-and-the-fr-4-extraction-test.md`, Notes**: replace "Decision: pdfplumber is the default; pypdf is kept only if it has fewer broken words in the 5-slide sample (AD-9)." with "Decision: the user chose pypdf 7.1.1 on 2026-11-19 because column order changes meaning; both libraries had 0 broken words (AD-9, changed)."

**`tickets.toml`** (epic description): "...then pdf_text.py extracts it with pypdf (chosen over pdfplumber after the comparison)..."

**`story-lectures-are-private-to-their-owner.md`** (AC about the import boundary, already built and merged): leave as it is. The test now enforces pypdf instead of pdfplumber.
