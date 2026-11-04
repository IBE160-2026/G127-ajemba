from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from unittest import mock

from . import throttle


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


STRONG_PASSWORD = "Tulip-Orbit-4821-xy"
TEST_ADDRESS = "10.0.0.1"


def make_user(email="amara@example.com", password=STRONG_PASSWORD):
    return get_user_model().objects.create_user(email=email, password=password)


def log_in(client, email, password, address=TEST_ADDRESS, **extra):
    return client.post(
        reverse("login"), {"username": email, "password": password, **extra}, REMOTE_ADDR=address
    )


class RegisterTests(TestCase):
    def test_fr1_register_logs_in_and_lands_on_my_lectures(self):
        """FR-1, story 1.2 AC 1."""
        response = self.client.post(
            reverse("register"), {"email": "New@Example.com", "password": STRONG_PASSWORD}
        )
        self.assertRedirects(response, reverse("lectures"))
        self.assertTrue(get_user_model().objects.filter(email="new@example.com").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_fr1_register_rejects_duplicate_email(self):
        """FR-1, story 1.2 AC 2: Amara@Example.com is the same account as amara@example.com."""
        make_user("amara@example.com")
        response = self.client.post(
            reverse("register"), {"email": "Amara@Example.com", "password": STRONG_PASSWORD}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This email is already in use")
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_fr1_password_is_hashed(self):
        """FR-1, story 1.2 AC 3: the stored password is a hash."""
        self.client.post(reverse("register"), {"email": "h@example.com", "password": STRONG_PASSWORD})
        stored = get_user_model().objects.get(email="h@example.com").password
        self.assertTrue(stored.startswith("pbkdf2_sha256$"))
        self.assertNotIn(STRONG_PASSWORD, stored)

    def test_fr1_weak_passwords_are_refused_with_the_validator_message(self):
        """FR-1, story 1.2 AC 4."""
        common = self.client.post(reverse("register"), {"email": "a@example.com", "password": "password"})
        self.assertContains(common, "This password is too common.")
        short = self.client.post(reverse("register"), {"email": "b@example.com", "password": "Ab1!x"})
        self.assertContains(short, "This password is too short.")
        self.assertEqual(get_user_model().objects.count(), 0)


class LoginTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = make_user()

    def test_login_works_and_email_case_does_not_matter(self):
        response = log_in(self.client, "  AMARA@example.com ", STRONG_PASSWORD)
        self.assertRedirects(response, "/", fetch_redirect_response=False)
        self.assertIn("_auth_user_id", self.client.session)

    def test_wrong_password_gives_one_message_that_does_not_name_the_cause(self):
        response = log_in(self.client, "amara@example.com", "wrong")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct email and password")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_fr1_login_blocked_after_five_failures(self):
        """FR-1, story 1.2 AC 5, with a fixed clock (throttle.now is replaced)."""
        with mock.patch.object(throttle, "now", return_value=1_000_000.0):
            for _ in range(5):
                log_in(self.client, "amara@example.com", "wrong")
            blocked = log_in(self.client, "amara@example.com", STRONG_PASSWORD)
            self.assertContains(blocked, "Too many failed log-in attempts")
            self.assertNotIn("_auth_user_id", self.client.session)

            # Same email from another address is counted on its own.
            other = log_in(self.client, "amara@example.com", STRONG_PASSWORD, address="10.0.0.2")
            self.assertEqual(other.status_code, 302)
            self.client.logout()

        # Just inside 15 minutes: still blocked. Just after: allowed again.
        with mock.patch.object(throttle, "now", return_value=1_000_000.0 + 14 * 60):
            self.assertContains(
                log_in(self.client, "amara@example.com", STRONG_PASSWORD), "Too many failed log-in attempts"
            )
        with mock.patch.object(throttle, "now", return_value=1_000_000.0 + 15 * 60 + 1):
            again = log_in(self.client, "amara@example.com", STRONG_PASSWORD)
            self.assertEqual(again.status_code, 302)
            self.assertIn("_auth_user_id", self.client.session)

    def test_unknown_email_is_limited_the_same_way(self):
        """The limit gives no hint about which emails have an account."""
        with mock.patch.object(throttle, "now", return_value=5_000.0):
            for _ in range(5):
                log_in(self.client, "nobody@example.com", "wrong")
            self.assertContains(log_in(self.client, "nobody@example.com", "wrong"), "Too many failed")

    def test_a_good_login_clears_the_failures(self):
        with mock.patch.object(throttle, "now", return_value=7_000.0):
            for _ in range(4):
                log_in(self.client, "amara@example.com", "wrong")
            self.assertEqual(log_in(self.client, "amara@example.com", STRONG_PASSWORD).status_code, 302)
            self.client.logout()
            for _ in range(4):
                log_in(self.client, "amara@example.com", "wrong")
            self.assertEqual(log_in(self.client, "amara@example.com", STRONG_PASSWORD).status_code, 302)

    def test_login_next_must_be_same_host(self):
        """AD-7, story 1.2 AC 7."""
        for unsafe in ("https://evil.example/", "//evil.example/", "http://testserver.evil.example/"):
            response = log_in(self.client, "amara@example.com", STRONG_PASSWORD, next=unsafe)
            self.assertRedirects(response, "/", fetch_redirect_response=False)
            self.client.logout()
        safe = log_in(self.client, "amara@example.com", STRONG_PASSWORD, next="/lectures/")
        self.assertRedirects(safe, "/lectures/", fetch_redirect_response=False)


class LogoutTests(TestCase):
    def setUp(self):
        cache.clear()
        make_user()
        log_in(self.client, "amara@example.com", STRONG_PASSWORD)

    def test_logout_requires_post(self):
        """AD-19.2, story 1.2 AC 6: a GET does not log out."""
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertEqual(self.client.get(reverse("lectures")).status_code, 200)

    def test_fr1_protected_page_redirects_after_logout(self):
        """FR-1/FR-2, story 1.2 AC 6."""
        self.assertEqual(self.client.get(reverse("lectures")).status_code, 200)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        after = self.client.get(reverse("lectures"))
        self.assertRedirects(after, "/accounts/login/?next=/lectures/", fetch_redirect_response=False)
        self.assertNotContains(after, "No lectures yet", status_code=302)

    def test_logged_in_responses_are_no_store_and_logged_out_pages_are_not(self):
        """AD-19.3, story 1.2 AC 6."""
        self.assertEqual(self.client.get(reverse("lectures"))["Cache-Control"], "no-store")
        self.client.post(reverse("logout"))
        self.assertNotIn("no-store", self.client.get(reverse("home")).get("Cache-Control", ""))
