"""The only way for views to get a lecture (AD-8)."""

from django.http import Http404

from .models import Lecture


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
