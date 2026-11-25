from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render

from core import jobs

from . import notice
from .services import (
    MSG_TOO_BIG,
    RetryRefused,
    UploadRejected,
    acknowledge_notice,
    create_lecture_from_upload,
    get_lecture,
    get_lecture_for_write,
    get_summary,
    reap_stale,
    retry_lecture,
    notice_is_current,
    uploads_left_today,
)


@login_required
def lecture_detail(request, lecture_id):
    """The Processing page while the lecture is processing or failed (AD-11). The Summary page
    replaces the Ready part in story 3.4."""
    reap_stale()
    lecture = get_lecture(request.user, lecture_id)
    if lecture.status == "ready":
        return redirect("lecture_summary", lecture_id=lecture.id)
    return render(request, "lectures/detail.html", {"lecture": lecture, "poll_seconds": settings.POLL_SECONDS})


@login_required
def lecture_summary(request, lecture_id):
    """The Summary page (FR-8, FR-9, FR-11). Owner only: a wrong owner and a missing id give the
    same 404. A lecture that is not ready goes to its Processing page. No AI call is made here."""
    reap_stale()
    lecture, parts = get_summary(request.user, lecture_id)
    if lecture.status != "ready":
        return redirect("lecture_detail", lecture_id=lecture.id)
    return render(request, "lectures/summary.html", {"lecture": lecture, "parts": parts})


@login_required
def retry(request, lecture_id):
    """Try a failed lecture again, at most 3 times. The owner check comes before the method check."""
    get_lecture_for_write(request.user, lecture_id)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        with transaction.atomic():
            retry_lecture(request.user, lecture_id)
            jobs.enqueue(jobs.SUMMARY, lecture_id)
    except RetryRefused as refused:
        lecture = get_lecture(request.user, lecture_id)
        context = {"lecture": lecture, "poll_seconds": settings.POLL_SECONDS, "error": str(refused)}
        return render(request, "lectures/detail.html", context, status=400)
    return redirect("lecture_detail", lecture_id=lecture_id)


@login_required
def upload(request):
    """Upload one PDF. All checks live in the service; a rejection shows its message (AD-20)."""
    error = ""
    if request.method == "POST":
        uploaded = request.FILES.get("pdf")
        if request.POST.get("notice_ack") and not notice_is_current(request.user):
            acknowledge_notice(request.user)  # stored at once, whatever happens to the file
        try:
            if getattr(request, "upload_too_big", False):
                raise UploadRejected(MSG_TOO_BIG)  # the upload handler stopped reading at 10 MB + 1
            lecture = create_lecture_from_upload(request.user, uploaded)
        except UploadRejected as rejected:
            error = str(rejected)
        else:
            jobs.enqueue(jobs.SUMMARY, lecture.id)  # runs after the commit (AD-3.4)
            return redirect("lecture_detail", lecture_id=lecture.id)
        finally:
            # Django's own temporary copy of the upload is removed on every path.
            if uploaded is not None:
                uploaded.close()
    context = {
        "error": error,
        "notice": notice,
        "show_notice": not notice_is_current(request.user),
        "uploads_per_day": settings.UPLOADS_PER_DAY,
        "uploads_left": uploads_left_today(request.user),
    }
    return render(request, "lectures/upload.html", context, status=400 if error else 200)
