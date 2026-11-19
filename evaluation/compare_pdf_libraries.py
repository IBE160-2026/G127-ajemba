# Needs both pypdf==7.1.1 (it is in requirements.txt) and pdfplumber==0.11.10 (install it
# separately: pip install pdfplumber==0.11.10). It is NOT part of the app: pdfplumber is not in
# requirements.txt and no app code may import it (see core/tests.py).
#
# Compares pdfplumber and pypdf on one PDF (FR-4, AD-9). Run it from the project folder:
#   .venv/Scripts/python evaluation/compare_pdf_libraries.py [pdf] [page numbers, 1-based]
# Default: evaluation/testset/test-lecture-1.pdf and the sample slides chosen below.
"""Count broken words per library on a sample of slides and print the average characters per page."""

import re
import sys
from pathlib import Path

import pdfplumber
import pypdf

DEFAULT_PDF = Path(__file__).parent / "testset" / "test-lecture-1.pdf"
# Slides with the hardest layouts: columns (3, 5, 8, 10), numbered steps (6).
DEFAULT_SAMPLE = [3, 5, 6, 8, 10]

LIGATURES = re.compile("[\ufb00-\ufb06]")
HYPHEN_BREAK = re.compile(r"\w-\n\w")
# A lower-case letter directly followed by an upper-case one inside a token: "handHygiene".
RUN_TOGETHER = re.compile(r"\b\w*[a-z][A-Z]\w*\b")
REPLACEMENT = re.compile("\ufffd")


def extract_plumber(path):
    with pdfplumber.open(path) as document:
        return [page.extract_text() or "" for page in document.pages]


def extract_pypdf(path):
    return [page.extract_text() or "" for page in pypdf.PdfReader(str(path)).pages]


def broken_words(text):
    return {
        "hyphenated line breaks": len(HYPHEN_BREAK.findall(text)),
        "run-together words": len(RUN_TOGETHER.findall(text)),
        "ligature glyphs": len(LIGATURES.findall(text)),
        "replacement characters": len(REPLACEMENT.findall(text)),
    }


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_PDF
    sample = [int(n) for n in argv[2:]] or DEFAULT_SAMPLE
    results = {"pdfplumber": extract_plumber(path), "pypdf": extract_pypdf(path)}
    print(f"File: {path}  pypdf {pypdf.__version__}  pdfplumber {pdfplumber.__version__}")
    for name, pages in results.items():
        average = sum(len(p) for p in pages) / len(pages)
        picked = "\n".join(pages[n - 1] for n in sample)
        print(f"\n== {name}: {len(pages)} pages, average {average:.1f} characters per page")
        print(f"   sample slides {sample}:", broken_words(picked))
        print("   all pages:", broken_words("\n".join(pages)))
    for n in sample:
        for name, pages in results.items():
            print(f"\n--- slide {n} / {name} ---\n{pages[n - 1]}")


if __name__ == "__main__":
    main(sys.argv)
