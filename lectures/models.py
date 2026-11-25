from django.conf import settings
from django.db import models
from django.utils import timezone


class LectureQuerySet(models.QuerySet):
    def for_user(self, user):
        """The one door to lectures (AD-8.1): only rows owned by this user.

        A logged-out visitor owns nothing. Example lectures have no owner, so they
        never show up here; the Example Lecture exception is added in epic-demo-readme.
        """
        if user is None or not getattr(user, "is_authenticated", False):
            return self.none()
        return self.filter(user=user)


class Lecture(models.Model):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    LANGUAGES = [("en", "English"), ("nb", "Norwegian")]

    # Empty only for example lectures (AD-10.5, AD-17).
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="lectures",
    )
    is_example = models.BooleanField(default=False)
    example_key = models.CharField(max_length=100, null=True, blank=True, unique=True)
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=2, choices=LANGUAGES, default="en")
    # Changed only through services.set_status() (AD-3.5).
    status = models.CharField(max_length=20, default=PROCESSING)
    status_changed_at = models.DateTimeField(default=timezone.now)
    retry_count = models.PositiveSmallIntegerField(default=0)
    generated_with = models.CharField(max_length=100, blank=True, default="")

    objects = LectureQuerySet.as_manager()

    def __str__(self):
        return self.title


class PageTextQuerySet(models.QuerySet):
    def for_user(self, user):
        """The one door to page text (AD-8.1): only pages of lectures this user owns."""
        if user is None or not getattr(user, "is_authenticated", False):
            return self.none()
        return self.filter(lecture__user=user)


class PageText(models.Model):
    """Text of one PDF page. The PDF itself is never stored (AD-20)."""

    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="pages")
    number = models.PositiveSmallIntegerField()  # 1-based slide number
    text = models.TextField(blank=True, default="")

    objects = PageTextQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["lecture", "number"], name="unique_page_per_lecture")
        ]
        ordering = ["number"]


class UploadLogQuerySet(models.QuerySet):
    def for_user(self, user):
        """The one door to the upload count (AD-8.1): only this user's rows."""
        if user is None or not getattr(user, "is_authenticated", False):
            return self.none()
        return self.filter(user=user)


class UploadLog(models.Model):
    """One row per accepted upload (FR-7). No link to Lecture: deleting a lecture keeps the count."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="upload_logs")
    created_at = models.DateTimeField(default=timezone.now)  # UTC
    local_day = models.DateField()  # the date in LIMIT_TIME_ZONE when the upload was accepted

    objects = UploadLogQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["user", "local_day"], name="uploadlog_user_day")]


class AiCallLogQuerySet(models.QuerySet):
    def for_user(self, user):
        """The one door to the AI call log (AD-8.1): only this user's rows."""
        if user is None or not getattr(user, "is_authenticated", False):
            return self.none()
        return self.filter(user=user)


class AiCallLog(models.Model):
    """One row per AI call, never content (AD-4.11). Story 3.1 writes the rows; the budget check
    in services reads them (AD-23). No link to Lecture: deleting a lecture keeps the count."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_call_logs")
    task = models.CharField(max_length=50)
    model = models.CharField(max_length=100, blank=True, default="")
    prompt_version = models.CharField(max_length=50, blank=True, default="")
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    wait_seconds = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)  # UTC
    local_day = models.DateField()  # the date in LIMIT_TIME_ZONE, like UploadLog

    objects = AiCallLogQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["local_day"], name="aicalllog_day")]
