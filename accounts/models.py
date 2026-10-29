from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager, normalise_email


class User(AbstractBaseUser, PermissionsMixin):
    """Email-based user (AD-7). Every ownership link points to settings.AUTH_USER_MODEL."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    # Upload notice acknowledgement (AD-16); used by a later story.
    notice_ack_at = models.DateTimeField(null=True, blank=True)
    notice_version = models.CharField(max_length=20, blank=True, default="")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # Normalise here too, so no code path can store another form.
        self.email = normalise_email(self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
