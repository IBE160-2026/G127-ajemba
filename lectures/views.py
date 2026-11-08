from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_lecture


@login_required
def lecture_detail(request, lecture_id):
    """Stub page so the privacy tests have something to request. epic-summary replaces it."""
    lecture = get_lecture(request.user, lecture_id)
    return render(request, "lectures/detail.html", {"lecture": lecture})
