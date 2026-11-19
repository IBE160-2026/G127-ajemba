"""PDF text extraction behind one function (AD-9). The only module that imports pypdf."""

import pypdf


def extract_pages(pdf):
    """Return exactly one string per PDF page, in order.

    `pdf` is a path or a binary file object. A page with no readable text gives an empty
    string. Pages are never skipped, so index + 1 is always the slide number.
    """
    reader = pypdf.PdfReader(pdf)
    return [page.extract_text() or "" for page in reader.pages]


def average_chars_per_page(pages):
    """Average characters per page over all pages, empty ones included (FR-4)."""
    if not pages:
        return 0.0
    return sum(len(page) for page in pages) / len(pages)
