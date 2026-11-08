"""The generated URL-by-user test (AD-8.4, FR-2, SM-7).

It reads the address list from urls.py itself, so a newly added address is covered with no
edit here. To make a page public, add its URL name to PUBLIC_URL_NAMES on purpose.
"""

import re
import uuid

from django.conf import settings
from django.test import TestCase
from django.urls import URLPattern, URLResolver, get_resolver

from accounts.tests import STRONG_PASSWORD, make_user
from lectures.models import Lecture

# Pages a logged-out visitor may open. The Example Lecture exception is added in epic-demo-readme.
PUBLIC_URL_NAMES = {"home", "register", "login", "logout"}

SECRET_TITLE = "Quantum Cheese Lecture"
PARAM = re.compile(r"<(?:(?P<converter>[^>:]+):)?(?P<name>[^>]+)>")


def all_routes(patterns=None, prefix=""):
    """Yield (url name, route text) for every address in urls.py, includes followed."""
    for pattern in get_resolver().url_patterns if patterns is None else patterns:
        route = str(pattern.pattern)
        if isinstance(pattern, URLResolver):
            yield from all_routes(pattern.url_patterns, prefix + route)
        elif isinstance(pattern, URLPattern):
            yield pattern.name or prefix + route, prefix + route


def fill_in(route, lecture_id):
    """Replace <int:lecture_id>-style parts with sample values. Returns (url, has_params)."""
    if route.startswith("^") or "(?P" in route:
        raise AssertionError(f"Use path() with converters, not a regex, for {route!r}")
    samples = {
        "int": str(lecture_id),
        "str": "x",
        "slug": "x",
        "path": "x",
        "uuid": str(uuid.UUID(int=0)),
    }

    def sample(match):
        converter = match.group("converter") or "str"
        if converter not in samples:
            raise AssertionError(f"Add a sample value for the converter {converter!r} to this test")
        return samples[converter]

    url, count = PARAM.subn(sample, route)
    return "/" + url, count > 0


class EveryUrlAsOtherUserAndAnonymousTests(TestCase):
    def setUp(self):
        self.user_a = make_user("a@example.com")
        make_user("b@example.com")
        self.lecture = Lecture.objects.create(user=self.user_a, title=SECRET_TITLE)

    def test_the_walker_finds_the_lecture_address(self):
        """Guards this test against passing because it found nothing."""
        names = {name for name, _ in all_routes()}
        self.assertIn("lecture_detail", names)
        self.assertTrue(PUBLIC_URL_NAMES <= names)

    def test_fr2_every_url_as_other_user_and_anonymous(self):
        routes = list(all_routes())
        self.assertGreater(len(routes), 3)

        for name, route in routes:
            url, has_params = fill_in(route, self.lecture.id)
            methods = ["get", "post"] if has_params else ["get"]
            public = name in PUBLIC_URL_NAMES

            # Logged out.
            for method in methods:
                with self.subTest(who="anonymous", method=method, url=url):
                    response = getattr(self.client, method)(url)
                    self.assertNotIn(SECRET_TITLE, response.content.decode())
                    if not public:
                        self.assertEqual(response.status_code, 302)
                        self.assertTrue(response["Location"].startswith(settings.LOGIN_URL))

            # Logged in as user B, asking with user A's ids.
            self.client.login(email="b@example.com", password=STRONG_PASSWORD)
            for method in methods:
                with self.subTest(who="user B", method=method, url=url):
                    response = getattr(self.client, method)(url)
                    self.assertLess(response.status_code, 500)
                    self.assertNotIn(SECRET_TITLE, response.content.decode())
                    if has_params and not public:
                        self.assertEqual(response.status_code, 404)
            self.client.logout()
