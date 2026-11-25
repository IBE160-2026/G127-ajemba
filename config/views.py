from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from lectures.models import Lecture
from lectures.services import get_lecture, reap_stale


def home(request):
    return render(request, "home.html")


@login_required
def lectures(request):
    """My lectures. Only the user's own lectures, through the owner-scoped manager (AD-8.1)."""
    reap_stale()
    context = {"lectures": Lecture.objects.for_user(request.user).order_by("-id"), "poll_seconds": settings.POLL_SECONDS}
    return render(request, "lectures.html", context)


@login_required
def lecture_status(request, lecture_id):
    """The one status address, /status/lecture/<id>/ (AD-11.1). htmx polls it; a normal visit
    gets the whole page. `?row=1` is the short form used inside the list."""
    reap_stale()
    lecture = get_lecture(request.user, lecture_id)  # wrong owner and missing id: the same 404
    context = {"lecture": lecture, "poll_seconds": settings.POLL_SECONDS}
    if request.headers.get("HX-Request"):
        template = "lectures/_status_row.html" if request.GET.get("row") else "lectures/_status.html"
        return render(request, template, context)
    return render(request, "lectures/detail.html", context)
