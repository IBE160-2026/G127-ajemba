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
    # Status values and set_status() are added with the processing story.
    status = models.CharField(max_length=20, default="processing")
    status_changed_at = models.DateTimeField(default=timezone.now)
    retry_count = models.PositiveSmallIntegerField(default=0)
    generated_with = models.CharField(max_length=100, blank=True, default="")

    objects = LectureQuerySet.as_manager()

    def __str__(self):
        return self.title
