"""Creates the PDF fixtures that tests cannot build themselves.

Only core/pdf_text.py may import pypdf in the app (AD-2.4); evaluation/ is exempt, so the
encrypted fixture is made here, once, and committed. Run: .venv/Scripts/python evaluation/make_test_fixtures.py
"""

from pathlib import Path

import pypdf

OUT = Path(__file__).resolve().parent.parent / "lectures" / "test_fixtures"


def make_encrypted_pdf():
    writer = pypdf.PdfWriter()
    writer.add_blank_page(300, 200)
    writer.encrypt("secret")
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "encrypted.pdf", "wb") as handle:
        writer.write(handle)


if __name__ == "__main__":
    make_encrypted_pdf()
