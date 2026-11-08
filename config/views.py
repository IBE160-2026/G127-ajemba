from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from lectures.models import Lecture


def home(request):
    return render(request, "home.html")


@login_required
def lectures(request):
    """My lectures. Only the user's own lectures, through the owner-scoped manager (AD-8.1)."""
    return render(request, "lectures.html", {"lectures": Lecture.objects.for_user(request.user)})
