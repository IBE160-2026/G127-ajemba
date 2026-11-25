"""Story 3.4: the Summary page (FR-8, FR-9, FR-11, AD-5, AD-8). No key, no network, no AI call."""

import io
import re
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from accounts.tests import make_user
from lectures.models import KeyTerm, Lecture, PageText, SummaryPart

from .test_processing import make_lecture
from .test_summary_job import no_real_calls

BASE = Path(settings.BASE_DIR)


def ready_lecture(user, parts=None, title="Databases", pages=16):
    lecture = make_lecture(user, title, status=Lecture.READY)
    PageText.objects.bulk_create([PageText(lecture=lecture, number=i, text=f"slide {i}") for i in range(1, pages + 1)])
    parts = parts or [
        {"heading": "Why we normalise", "text": "First idea.\nSecond idea.", "refs": [12, 13, 14, 15],
         "terms": [("Redundancy", "The same data is stored more than once.")]},
        {"heading": "Normal forms", "text": "Forms.", "refs": [3, 7, 12], "terms": []},
    ]
    for order, p in enumerate(parts, 1):
        row = SummaryPart.objects.create(lecture=lecture, order=order, heading=p["heading"], text=p["text"], source_refs=p["refs"])
        for term, explanation in p["terms"]:
            KeyTerm.objects.create(summary_part=row, term=term, explanation=explanation)
    return lecture


class SummaryPageTests(TestCase):
    def setUp(self):
        no_real_calls(self)
        self.user = make_user("a@example.com")
        self.client.force_login(self.user)
        self.lecture = ready_lecture(self.user)
        self.url = reverse("lecture_summary", args=[self.lecture.id])

    def test_fr8_every_part_shows_source_reference(self):
        html = self.client.get(self.url).content.decode()
        for expected in ("Why we normalise", "First idea.", "Second idea.", "Slides 12 to 15", "Slides 3, 7 and 12"):
            self.assertIn(expected, html)
        self.assertIn('aria-label="Slides 12 to 15, Why we normalise"', html)
        self.assertIn("<title>Summary – Databases – Recall</title>", html)

    def test_fr9_key_terms_with_explanations_shown(self):
        html = self.client.get(self.url).content.decode()
        self.assertIn("Redundancy", html)
        self.assertIn("The same data is stored more than once.", html)

    def test_fr11_ai_notice_on_summary_page(self):
        html = self.client.get(self.url).content.decode()
        self.assertIn("This text was made by AI. It can contain mistakes. Check it against your slides.", html)

    def test_ad5_ai_text_is_escaped(self):
        bad = [{"heading": "<script>alert(1)</script>", "text": "<script>alert(2)</script>", "refs": [1],
                "terms": [("<b>x</b>", "<img src=x onerror=alert(3)>")]}]
        lecture = ready_lecture(self.user, bad, "Evil")
        html = self.client.get(reverse("lecture_summary", args=[lecture.id])).content.decode()
        self.assertNotIn("<script>alert", html)
        self.assertNotIn("<img src=x", html)
        self.assertNotIn("<b>x</b>", html)
        self.assertIn("&lt;script&gt;alert(2)&lt;/script&gt;", html)

    def test_ad5_no_safe_filter_in_templates(self):
        forbidden = re.compile(r"\|\s*safe\b|mark_safe|autoescape\s+off|markdown|safeseq|format_html", re.I)
        files = list((BASE / "templates").rglob("*.html"))
        files += [p for app in ("lectures", "core", "config", "accounts") for p in (BASE / app).rglob("*.py")
                  if not p.name.startswith("test")]
        self.assertTrue(files)
        for path in files:
            self.assertIsNone(forbidden.search(path.read_text(encoding="utf-8")), str(path))

    def test_summary_page_owner_only(self):
        other = make_user("b@example.com")
        self.client.force_login(other)
        wrong = self.client.get(self.url)
        missing = self.client.get(reverse("lecture_summary", args=[self.lecture.id + 1000]))
        self.assertEqual(wrong.status_code, 404)
        def body(response):  # the page carries a fresh CSRF token each time; nothing else may differ
            return re.sub(rb'[A-Za-z0-9]{32,}', b'TOKEN', response.content)

        self.assertEqual(body(wrong), body(missing))
        self.assertNotIn("Why we normalise", wrong.content.decode())
        self.client.logout()
        anonymous = self.client.get(self.url)
        self.assertEqual(anonymous.status_code, 302)
        self.assertIn("/login", anonymous["Location"])

    def test_terms_stay_under_their_own_part_and_lang_is_set(self):
        html = self.client.get(self.url).content.decode()
        first, second = html.split('id="part-2"')
        self.assertIn("Redundancy", first)
        self.assertNotIn("Redundancy", second)
        self.assertIn("This part has no key terms.", second)
        self.assertIn('lang="en"', html)
        self.assertIn('href="#part-2"', html)

    def test_ready_status_fragment_links_to_summary(self):
        html = self.client.get(reverse("lecture_status", args=[self.lecture.id]), HTTP_HX_REQUEST="true").content.decode()
        self.assertIn(self.url, html)

    def test_failed_goes_to_processing_page(self):
        failed = make_lecture(self.user, "Failed", status=Lecture.FAILED)
        response = self.client.get(reverse("lecture_summary", args=[failed.id]))
        self.assertRedirects(response, reverse("lecture_detail", args=[failed.id]))

    def test_not_ready_goes_to_processing_page(self):
        busy = make_lecture(self.user, "Busy")
        response = self.client.get(reverse("lecture_summary", args=[busy.id]))
        self.assertRedirects(response, reverse("lecture_detail", args=[busy.id]))

    def test_ready_detail_goes_to_summary(self):
        response = self.client.get(reverse("lecture_detail", args=[self.lecture.id]))
        self.assertRedirects(response, self.url)

    def test_page_makes_no_ai_call(self):
        # no_real_calls makes the provider transport raise; the page must still load.
        self.assertEqual(self.client.get(self.url).status_code, 200)


class CheckSummaryTests(TestCase):
    def test_check_summary_finds_missing_slides(self):
        user = make_user("c@example.com")
        good = ready_lecture(user)
        out = io.StringIO()
        call_command("check_summary", good.id, stdout=out)
        self.assertIn("OK", out.getvalue())
        bad = ready_lecture(user, [{"heading": "H", "text": "t", "refs": [99], "terms": []}], "Bad", pages=5)
        with self.assertRaises(CommandError):
            call_command("check_summary", bad.id)
        empty = make_lecture(user, "Empty", status=Lecture.READY)
        with self.assertRaises(CommandError):
            call_command("check_summary", empty.id)


class TimingRecordTests(TestCase):
    def test_readme_and_timing_record_exist(self):
        readme = (BASE / "README.md").read_text(encoding="utf-8")
        self.assertIn("31 to 50", readme)
        self.assertIn("docs/summary-timing.md", readme)
        self.assertTrue((BASE / "docs" / "summary-timing.md").exists())
