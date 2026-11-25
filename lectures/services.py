"""The only way for views to get a lecture (AD-8)."""

import json
import os
import subprocess
import sys
import tempfile
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import Http404
from django.utils import timezone

from core.pdf_text import average_chars_per_page

from .models import AiCallLog, Lecture, PageText, UploadLog
from .notice import NOTICE_VERSION


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
MSG_NOTICE = "Tick the box to confirm you have read the notice."
MSG_AI_BUDGET = "Recall has used up its AI budget for today. Please try again tomorrow."
MSG_RETRY_LIMIT = "This lecture has already been tried again 3 times. Please upload the file again."
MSG_RETRY_NOT_FAILED = "Only a lecture that failed can be tried again."

_CHUNK = 64 * 1024
_EXTRACT_CLI = Path(__file__).resolve().parent.parent / "core" / "extract_cli.py"


class UploadRejected(Exception):
    """A check failed. The message is the plain text shown to the student."""


def limit_message():
    return f"You have used your {settings.UPLOADS_PER_DAY} uploads for today. You can upload again tomorrow."


# --- Notice (FR-6, AD-16) and daily limit (FR-7) -----------------------------------------------

def notice_is_current(user):
    """True when the user acknowledged the current notice version."""
    return user.notice_ack_at is not None and user.notice_version == str(NOTICE_VERSION)


def acknowledge_notice(user):
    """Store the acknowledgement of the current notice. Only ever called with request.user."""
    user.notice_ack_at = timezone.now()
    user.notice_version = str(NOTICE_VERSION)
    user.save(update_fields=["notice_ack_at", "notice_version"])


def _now():
    """The one clock for the daily limit; tests replace it with a fixed time."""
    return timezone.now()


def local_today():
    """Today's date in LIMIT_TIME_ZONE. A new day starts at local midnight."""
    return _now().astimezone(ZoneInfo(settings.LIMIT_TIME_ZONE)).date()


def uploads_left_today(user):
    used = UploadLog.objects.for_user(user).filter(local_day=local_today()).count()
    return max(settings.UPLOADS_PER_DAY - used, 0)


# --- Status changes (AD-3.5 to AD-3.7) -------------------------------------------------------

ALLOWED_CHANGES = {
    (Lecture.PROCESSING, Lecture.READY),
    (Lecture.PROCESSING, Lecture.FAILED),
    (Lecture.FAILED, Lecture.PROCESSING),  # retry
}


def set_status(lecture, from_states, to_state):
    """Change the status only if it is still one of `from_states`; return whether it changed.

    One conditional UPDATE, so of two callers only one gets True. A caller that gets False stops.
    """
    from_states = list(from_states)
    for state in from_states:
        if (state, to_state) not in ALLOWED_CHANGES:
            raise ValueError(f"The change {state} -> {to_state} is not allowed.")
    changed = Lecture.objects.filter(pk=lecture.pk, status__in=from_states).update(
        status=to_state, status_changed_at=timezone.now()
    )
    if changed:
        lecture.status = to_state
    return bool(changed)


def reap_stale():
    """A lecture in `processing` longer than STALE_MINUTES becomes `failed`. Returns how many."""
    cutoff = timezone.now() - timedelta(minutes=settings.STALE_MINUTES)
    return Lecture.objects.filter(status=Lecture.PROCESSING, status_changed_at__lt=cutoff).update(
        status=Lecture.FAILED, status_changed_at=timezone.now()
    )


class RetryRefused(Exception):
    """The retry was not allowed. The message is the plain text shown to the student."""


def retry_lecture(user, lecture_id):
    """failed -> processing, at most RETRY_LIMIT times per lecture; adds no upload row (AD-15.5).

    Owner check first (same bare 404), then the AI budget, then one conditional UPDATE.
    """
    lecture = get_lecture_for_write(user, lecture_id)
    reap_stale()
    lecture.refresh_from_db()
    if lecture.status != Lecture.FAILED:
        raise RetryRefused(MSG_RETRY_NOT_FAILED)
    if lecture.retry_count >= settings.RETRY_LIMIT:
        raise RetryRefused(MSG_RETRY_LIMIT)
    if not ai_budget_left(user):
        raise RetryRefused(MSG_AI_BUDGET)
    changed = Lecture.objects.filter(
        pk=lecture.pk, status=Lecture.FAILED, retry_count__lt=settings.RETRY_LIMIT
    ).update(status=Lecture.PROCESSING, status_changed_at=timezone.now(), retry_count=F("retry_count") + 1)
    if not changed:
        raise RetryRefused(MSG_RETRY_LIMIT)
    lecture.refresh_from_db()
    return lecture


def ai_budget_left(user):
    """False when this user's or everybody's AI calls for today are used up (AD-23)."""
    today = local_today()
    todays = AiCallLog.objects.filter(local_day=today)
    if todays.count() >= settings.AI_CALLS_GLOBAL_PER_DAY:
        return False
    return AiCallLog.objects.for_user(user).filter(local_day=today).count() < settings.AI_CALLS_PER_USER_PER_DAY


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

    Raises UploadRejected with the student-facing message; a rejection creates nothing
    and is not counted toward the daily limit.
    The PDF is only ever a temporary file, deleted in `finally` (data minimisation).
    No PDF read happens inside atomic() (AD-24).
    """
    if not notice_is_current(user):  # FR-6: refused by the server before anything is read
        raise UploadRejected(MSG_NOTICE)
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
        # FR-7: count and insert in one transaction (the database starts it IMMEDIATE, AD-24).
        today = local_today()
        if UploadLog.objects.for_user(user).filter(local_day=today).count() >= settings.UPLOADS_PER_DAY:
            raise UploadRejected(limit_message())
        if not ai_budget_left(user):  # AD-20 step 5: nothing is created and no job is queued
            raise UploadRejected(MSG_AI_BUDGET)
        lecture = Lecture.objects.create(user=user, title=title, status=Lecture.PROCESSING)
        UploadLog.objects.create(user=user, local_day=today)
        PageText.objects.bulk_create(
            [PageText(lecture=lecture, number=i, text=t) for i, t in enumerate(pages, start=1)]
        )
    return lecture


def get_page_texts(user, lecture_id):
    """Page text of a lecture the user owns, through the owner-scoped door (AD-8)."""
    lecture = get_lecture(user, lecture_id)
    return PageText.objects.for_user(user).filter(lecture=lecture)
