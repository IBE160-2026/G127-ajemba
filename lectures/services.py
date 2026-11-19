"""The only way for views to get a lecture (AD-8)."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.http import Http404

from core.pdf_text import average_chars_per_page

from .models import Lecture, PageText


def get_lecture(user, lecture_id):
    """A lecture the user owns. Wrong owner and missing id give the same bare 404 (AD-8.2)."""
    try:
        return Lecture.objects.for_user(user).get(pk=lecture_id)
    except Lecture.DoesNotExist:
        raise Http404() from None


def get_lecture_for_write(user, lecture_id):
    """Door for every mutating endpoint (AD-8.3). Example rows are refused with the same 404."""
    lecture = get_lecture(user, lecture_id)
    if lecture.is_example:
        raise Http404()
    return lecture


# --- Upload (AD-20) -------------------------------------------------------------------------

MSG_NO_FILE = "Choose a PDF file."
MSG_TOO_BIG = "This file is larger than 10 MB. Choose a smaller file."
MSG_NOT_PDF = "This file is not a PDF. Choose a PDF file."
MSG_TOO_LONG = "This PDF has more than 50 pages. Choose a shorter file."
MSG_NO_TEXT = "This file has no text we can read. Choose a PDF with text, not a scan."

_CHUNK = 64 * 1024
_EXTRACT_CLI = Path(__file__).resolve().parent.parent / "core" / "extract_cli.py"


class UploadRejected(Exception):
    """A check failed. The message is the plain text shown to the student."""


def _copy_with_limit(uploaded, target):
    """Copy the upload into `target`, reading at most UPLOAD_MAX_BYTES + 1 bytes (step 1)."""
    limit = settings.UPLOAD_MAX_BYTES
    total = 0
    while total <= limit:
        chunk = uploaded.read(min(_CHUNK, limit + 1 - total))
        if not chunk:
            break
        target.write(chunk)
        total += len(chunk)
    if total > limit:
        raise UploadRejected(MSG_TOO_BIG)


def _extract_in_subprocess(path):
    """Step 3: extract in a separate process with a time limit. Any failure means no text."""
    try:
        result = subprocess.run(
            [sys.executable, "-I", str(_EXTRACT_CLI), str(path)],
            capture_output=True,
            timeout=settings.PDF_EXTRACT_TIMEOUT_SECONDS,
        )
        # On timeout, subprocess.run kills the child before raising.
        if result.returncode != 0:
            raise UploadRejected(MSG_NO_TEXT)
        pages = json.loads(result.stdout.decode("utf-8"))
    except (subprocess.TimeoutExpired, ValueError, OSError):
        raise UploadRejected(MSG_NO_TEXT) from None
    if not isinstance(pages, list) or not all(isinstance(p, str) for p in pages):
        raise UploadRejected(MSG_NO_TEXT)
    return pages


def create_lecture_from_upload(user, uploaded):
    """Run the checks in order, then create the Lecture and its PageText rows.

    Raises UploadRejected with the student-facing message; a rejection creates nothing.
    The PDF is only ever a temporary file, deleted in `finally` (data minimisation).
    No PDF read happens inside atomic() (AD-24).
    """
    if uploaded is None:
        raise UploadRejected(MSG_NO_FILE)
    fd, temp_path = tempfile.mkstemp(suffix=".pdf", dir=settings.FILE_UPLOAD_TEMP_DIR)
    try:
        with os.fdopen(fd, "wb") as target:
            _copy_with_limit(uploaded, target)
        with open(temp_path, "rb") as check:
            if check.read(5) != b"%PDF-":
                raise UploadRejected(MSG_NOT_PDF)
        pages = _extract_in_subprocess(temp_path)
    finally:
        try:
            os.remove(temp_path)
        except FileNotFoundError:
            pass

    if len(pages) > settings.UPLOAD_MAX_PAGES:
        raise UploadRejected(MSG_TOO_LONG)
    if not pages or average_chars_per_page(pages) < settings.UPLOAD_MIN_CHARS_PER_PAGE:
        raise UploadRejected(MSG_NO_TEXT)

    title = Path(getattr(uploaded, "name", "") or "").stem.strip()[:200] or "Untitled lecture"
    with transaction.atomic():
        lecture = Lecture.objects.create(user=user, title=title, status="processing")
        PageText.objects.bulk_create(
            [PageText(lecture=lecture, number=i, text=t) for i, t in enumerate(pages, start=1)]
        )
    return lecture


def get_page_texts(user, lecture_id):
    """Page text of a lecture the user owns, through the owner-scoped door (AD-8)."""
    lecture = get_lecture(user, lecture_id)
    return PageText.objects.for_user(user).filter(lecture=lecture)
