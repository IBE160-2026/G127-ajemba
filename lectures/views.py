from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .services import MSG_TOO_BIG, UploadRejected, create_lecture_from_upload, get_lecture


@login_required
def lecture_detail(request, lecture_id):
    """Stub page so the privacy tests have something to request. epic-summary replaces it."""
    lecture = get_lecture(request.user, lecture_id)
    return render(request, "lectures/detail.html", {"lecture": lecture})


@login_required
def upload(request):
    """Upload one PDF. All checks live in the service; a rejection shows its message (AD-20)."""
    error = ""
    if request.method == "POST":
        uploaded = request.FILES.get("pdf")
        try:
            if getattr(request, "upload_too_big", False):
                raise UploadRejected(MSG_TOO_BIG)  # the upload handler stopped reading at 10 MB + 1
            lecture = create_lecture_from_upload(request.user, uploaded)
        except UploadRejected as rejected:
            error = str(rejected)
        else:
            return redirect("lecture_detail", lecture_id=lecture.id)
        finally:
            # Django's own temporary copy of the upload is removed on every path.
            if uploaded is not None:
                uploaded.close()
    return render(request, "lectures/upload.html", {"error": error}, status=400 if error else 200)
