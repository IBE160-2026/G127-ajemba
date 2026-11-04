from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


@login_required
def lectures(request):
    """Placeholder My lectures page. Story 1.3 and epic-summary give it real content."""
    return render(request, "lectures.html")
