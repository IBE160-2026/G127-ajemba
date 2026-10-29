from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase


class EmailUserModelTests(TestCase):
    def test_fr1_email_is_normalised_and_unique(self):
        """FR-1, story 1.1 criteria 1 and 2."""
        User = get_user_model()
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.User")
        self.assertEqual(User._meta.label_lower, "accounts.user")
        self.assertEqual(User.USERNAME_FIELD, "email")

        user = User.objects.create_user(email="  Amara@Example.com ", password="a-long-test-pw-1")
        user.refresh_from_db()
        self.assertEqual(user.email, "amara@example.com")
        self.assertTrue(user.check_password("a-long-test-pw-1"))

        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(email="AMARA@example.com", password="another-test-pw-2")
        self.assertEqual(User.objects.count(), 1)

    def test_fr1_email_is_required(self):
        """FR-1: no account without an email address."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="   ", password="a-long-test-pw-1")
