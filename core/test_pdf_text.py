"""FR-4: one string per page, and text cleaning (AD-9, AD-21). Fixture PDFs are built here."""

import io

from django.test import SimpleTestCase

from core.pdf_text import average_chars_per_page, extract_pages
from core.text_utils import normalize_text


def make_pdf(pages):
    """Build a tiny PDF. Each item is a text line, or None for a page with no text at all."""
    objects = {}
    kids = []
    next_id = 4
    for text in pages:
        page_id = next_id
        next_id += 1
        if text is None:
            objects[page_id] = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] >>"
        else:
            content_id = next_id
            next_id += 1
            stream = f"BT /F1 14 Tf 20 100 Td ({text}) Tj ET"
            objects[content_id] = f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream"
            objects[page_id] = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] "
                f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>"
            )
        kids.append(f"{page_id} 0 R")
    objects[1] = "<< /Type /Catalog /Pages 2 0 R >>"
    objects[2] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>"
    objects[3] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    out = b"%PDF-1.4\n"
    offsets = {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out += f"{number} 0 obj\n{objects[number]}\nendobj\n".encode("latin-1")
    xref_at = len(out)
    out += f"xref\n0 {next_id}\n0000000000 65535 f \n".encode("ascii")
    for number in range(1, next_id):
        out += f"{offsets[number]:010d} 00000 n \n".encode("ascii")
    out += f"trailer\n<< /Size {next_id} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode("ascii")
    return io.BytesIO(out)


class ExtractPagesTests(SimpleTestCase):
    def test_fr4_extract_pages_one_string_per_page(self):
        pages = extract_pages(make_pdf(["First slide", "Second slide"]))
        self.assertEqual(pages, ["First slide", "Second slide"])

    def test_fr4_extract_pages_keeps_empty_page(self):
        pages = extract_pages(make_pdf(["Slide one", None, "Slide three"]))
        self.assertEqual(len(pages), 3)
        self.assertEqual(pages, ["Slide one", "", "Slide three"])

    def test_average_chars_per_page_counts_empty_pages(self):
        self.assertEqual(average_chars_per_page(["abcd", "", "ab"]), 2.0)
        self.assertEqual(average_chars_per_page([]), 0.0)


class NormalizeTextTests(SimpleTestCase):
    def test_normalize_text_ligatures_hyphens_whitespace(self):
        raw = "The \ufb01nal \ufb02ow  of exam-\nple and soft\u00adware and hy\u00ad\n  phen   today"
        self.assertEqual(normalize_text(raw), "the final flow of example and software and hyphen today")

    def test_normalize_text_case_folds(self):
        self.assertEqual(normalize_text("Hand HYGIENE Stra\u00dfe"), "hand hygiene strasse")
