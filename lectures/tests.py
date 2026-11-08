import re

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import TestCase
from django.urls import reverse

from accounts.tests import STRONG_PASSWORD, make_user

from .models import Lecture
from .services import get_lecture, get_lecture_for_write

SECRET_TITLE = "Quantum Cheese Lecture"


def mask_tokens(html):
    """CSRF tokens are new on every request; everything else must be identical."""
    return re.sub(r"[A-Za-z0-9]{32,64}", "TOKEN", html)


class OwnerScopedAccessTests(TestCase):
    def setUp(self):
        self.user_a = make_user("a@example.com")
        self.user_b = make_user("b@example.com")
        self.lecture = Lecture.objects.create(user=self.user_a, title=SECRET_TITLE)

    def test_sm7_for_user_finds_only_own_lectures(self):
        """Story 1.3 AC 1 (AD-8.1)."""
        self.assertEqual(list(Lecture.objects.for_user(self.user_a)), [self.lecture])
        self.assertEqual(list(Lecture.objects.for_user(self.user_b)), [])
        self.assertEqual(list(Lecture.objects.for_user(AnonymousUser())), [])
        self.assertEqual(list(Lecture.objects.for_user(None)), [])

    def test_sm7_owner_can_open_own_lecture(self):
        self.client.login(email="a@example.com", password=STRONG_PASSWORD)
        response = self.client.get(reverse("lecture_detail", args=[self.lecture.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, SECRET_TITLE)

    def test_sm7_user_b_cannot_read_user_a_lecture(self):
        """Story 1.3 AC 2: a wrong user and a missing id give the very same 404 page."""
        self.client.login(email="b@example.com", password=STRONG_PASSWORD)
        other = self.client.get(reverse("lecture_detail", args=[self.lecture.id]))
        missing = self.client.get(reverse("lecture_detail", args=[self.lecture.id + 1000]))

        self.assertEqual(other.status_code, 404)
        self.assertEqual(missing.status_code, 404)
        self.assertNotContains(other, SECRET_TITLE, status_code=404)
        self.assertEqual(
            mask_tokens(other.content.decode()), mask_tokens(missing.content.decode())
        )

    def test_sm7_logged_out_gets_redirect_and_no_data(self):
        """Story 1.3 AC 3: a logged-out visitor learns nothing, not even whether an id exists."""
        for lecture_id in (self.lecture.id, self.lecture.id + 1000):
            url = reverse("lecture_detail", args=[lecture_id])
            response = self.client.get(url)
            self.assertRedirects(
                response, f"/accounts/login/?next={url}", fetch_redirect_response=False
            )
            self.assertNotIn(SECRET_TITLE, response.content.decode())

        response = self.client.get(reverse("lectures"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(SECRET_TITLE, response.content.decode())

    def test_sm7_huge_id_gives_same_404_not_a_crash(self):
        """An id larger than the database can store must look like any other missing id."""
        huge = reverse("lecture_detail", args=[10**30])
        missing = reverse("lecture_detail", args=[self.lecture.id + 1000])
        self.client.login(email="b@example.com", password=STRONG_PASSWORD)
        response = self.client.get(huge)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            mask_tokens(response.content.decode()),
            mask_tokens(self.client.get(missing).content.decode()),
        )
        self.client.logout()
        self.assertEqual(self.client.get(huge).status_code, 302)

    def test_sm7_my_lectures_list_shows_only_own(self):
        self.client.login(email="b@example.com", password=STRONG_PASSWORD)
        self.assertNotContains(self.client.get(reverse("lectures")), SECRET_TITLE)
        self.client.login(email="a@example.com", password=STRONG_PASSWORD)
        self.assertContains(self.client.get(reverse("lectures")), SECRET_TITLE)

    def test_sm7_write_door_refuses_other_user_missing_id_and_example(self):
        """Story 1.3 AC 4 (AD-8.3): every refusal is the same Http404."""
        example = Lecture.objects.create(
            user=None, is_example=True, example_key="demo", title="Example"
        )
        self.assertEqual(get_lecture_for_write(self.user_a, self.lecture.id), self.lecture)
        for user, lecture_id in (
            (self.user_b, self.lecture.id),
            (self.user_a, self.lecture.id + 1000),
            (self.user_a, example.id),
            (self.user_b, example.id),
            (AnonymousUser(), self.lecture.id),
        ):
            with self.subTest(user=str(user), lecture_id=lecture_id):
                with self.assertRaises(Http404) as caught:
                    get_lecture_for_write(user, lecture_id)
                self.assertEqual(str(caught.exception), "")

    def test_sm7_read_door_gives_bare_404_for_wrong_owner(self):
        with self.assertRaises(Http404) as caught:
            get_lecture(self.user_b, self.lecture.id)
        self.assertEqual(str(caught.exception), "")
