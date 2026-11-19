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


# --- Story 2.2: upload with all checks (FR-3, FR-4, SM-8) -----------------------------------

import ast
import io
import os
import tempfile
import time
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from core.test_pdf_text import make_pdf

from . import services
from .models import PageText

GOOD_LINE = "Hand hygiene reduces infections in hospitals and clinics. " * 3  # > 100 chars


def pdf_bytes(pages):
    return make_pdf(pages).getvalue()


def upload_file(content, name="slides.pdf"):
    return SimpleUploadedFile(name, content, content_type="application/pdf")


class UploadTests(TestCase):
    def setUp(self):
        self.user = make_user("a@example.com")
        self.client.login(email="a@example.com", password=STRONG_PASSWORD)
        # Both the service copy and Django's own temporary upload file go here.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        override = override_settings(FILE_UPLOAD_TEMP_DIR=self.temp_dir.name)
        override.enable()
        self.addCleanup(override.disable)

    def post(self, content, name="slides.pdf"):
        return self.client.post(reverse("upload"), {"pdf": upload_file(content, name)})

    def assert_rejected(self, response, message):
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, message, status_code=400)
        self.assertEqual(Lecture.objects.count(), 0)
        self.assertEqual(PageText.objects.count(), 0)
        self.assertEqual(os.listdir(self.temp_dir.name), [], "a temporary file was left behind")

    def test_fr3_valid_upload_creates_lecture_with_page_rows(self):
        response = self.post(pdf_bytes([GOOD_LINE, GOOD_LINE, GOOD_LINE]), "Hygiene week 1.pdf")
        lecture = Lecture.objects.get()
        self.assertRedirects(response, reverse("lecture_detail", args=[lecture.id]))
        self.assertEqual((lecture.user, lecture.status, lecture.title), (self.user, "processing", "Hygiene week 1"))
        self.assertEqual(list(lecture.pages.values_list("number", flat=True)), [1, 2, 3])
        self.assertEqual(os.listdir(self.temp_dir.name), [])

    def test_fr3_rejects_file_over_10mb(self):
        big = b"%PDF-" + b"0" * (10 * 1024 * 1024)  # 10 MB + 5 bytes
        self.assert_rejected(self.post(big), "This file is larger than 10 MB. Choose a smaller file.")

    def test_fr3_upload_handler_stops_writing_at_10mb_plus_one_byte(self):
        from django.core.files.uploadhandler import SkipFile

        from .upload_handlers import LimitedTemporaryFileUploadHandler

        request = mock.Mock(spec=[])
        handler = LimitedTemporaryFileUploadHandler(request)
        handler.new_file("pdf", "huge.pdf", "application/pdf", 0)
        block, written = b"0" * (4 * 1024 * 1024), 0
        with self.assertRaises(SkipFile):
            for _ in range(10):  # 40 MB offered; the handler must refuse well before that
                handler.receive_data_chunk(block, written)
                written += len(block)
        self.assertEqual(handler.received, 10 * 1024 * 1024 + 1)
        self.assertTrue(request.upload_too_big)
        self.assertEqual(os.listdir(self.temp_dir.name), [])

    def test_fr3_reading_stops_at_10mb_plus_one_byte(self):
        class Counting(io.BytesIO):
            total = 0

            def read(self, size=-1):
                data = super().read(size)
                Counting.total += len(data)
                return data

        source = Counting(b"%PDF-" + b"0" * (30 * 1024 * 1024))
        source.name = "huge.pdf"
        with self.assertRaises(services.UploadRejected):
            services.create_lecture_from_upload(self.user, source)
        self.assertEqual(Counting.total, 10 * 1024 * 1024 + 1)
        self.assertEqual(os.listdir(self.temp_dir.name), [])

    def test_fr3_rejects_non_pdf(self):
        self.assert_rejected(self.post(b"PK\x03\x04 not a pdf", "slides.pdf"),
                             "This file is not a PDF. Choose a PDF file.")

    def test_fr3_rejects_over_50_pages(self):
        self.assert_rejected(self.post(pdf_bytes([GOOD_LINE] * 51)),
                             "This PDF has more than 50 pages. Choose a shorter file.")

    def test_fr3_accepts_exactly_50_pages(self):
        response = self.post(pdf_bytes([GOOD_LINE] * 50))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Lecture.objects.count(), 1)
        self.assertEqual(PageText.objects.count(), 50)

    def test_fr3_missing_file_gets_choose_message(self):
        response = self.client.post(reverse("upload"), {})
        self.assert_rejected(response, "Choose a PDF file.")

    NO_TEXT = "This file has no text we can read. Choose a PDF with text, not a scan."

    def test_fr4_rejects_image_only_pdf(self):
        self.assert_rejected(self.post(pdf_bytes([None, None, None])), self.NO_TEXT)

    def test_fr4_rejects_too_little_text_per_page(self):
        self.assert_rejected(self.post(pdf_bytes(["short", "short"])), self.NO_TEXT)

    def test_fr4_rejects_encrypted_and_corrupt_pdf(self):
        # encrypted.pdf is made by evaluation/make_test_fixtures.py (only evaluation/ may import pypdf).
        encrypted = (Path(__file__).parent / "test_fixtures" / "encrypted.pdf").read_bytes()
        self.assert_rejected(self.post(encrypted), self.NO_TEXT)
        self.assert_rejected(self.post(b"%PDF-1.4\n garbage that is not a pdf"), self.NO_TEXT)

    def test_extraction_timeout_gives_no_text_message(self):
        # A child that would run for a minute is stopped by the limit, not waited for.
        sleeper = Path(self.temp_dir.name).parent / "recall_sleeper_test.py"
        sleeper.write_text("import time\ntime.sleep(60)\n", encoding="utf-8")
        self.addCleanup(sleeper.unlink)
        started = time.monotonic()
        with override_settings(PDF_EXTRACT_TIMEOUT_SECONDS=1), mock.patch.object(
            services, "_EXTRACT_CLI", sleeper
        ):
            response = self.post(pdf_bytes([GOOD_LINE]))
        self.assertLess(time.monotonic() - started, 20)
        self.assert_rejected(response, self.NO_TEXT)

    def test_no_temp_file_left_when_extraction_crashes_unexpectedly(self):
        with mock.patch.object(services.subprocess, "run", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                services.create_lecture_from_upload(self.user, upload_file(pdf_bytes([GOOD_LINE])))
        self.assertEqual(os.listdir(self.temp_dir.name), [])
        self.assertEqual(Lecture.objects.count(), 0)

    def test_sm8_rejected_upload_creates_nothing_and_calls_no_ai(self):
        self.post(pdf_bytes([None]))
        self.assertEqual(Lecture.objects.count(), 0)
        root = Path(services.__file__).parent
        imported = set()
        for name in ("services.py", "views.py"):
            for node in ast.walk(ast.parse((root / name).read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    imported |= {a.name for a in node.names}
                elif isinstance(node, ast.ImportFrom):
                    imported.add(node.module or "")
        for module in imported:
            for banned in ("ai_client", "genai", "google", "openai", "anthropic"):
                self.assertNotIn(banned, module)

    def test_sm7_page_text_is_owner_scoped_with_uniform_404(self):
        self.post(pdf_bytes([GOOD_LINE, GOOD_LINE]))
        lecture = Lecture.objects.get()
        other = make_user("b@example.com")
        self.assertEqual(services.get_page_texts(self.user, lecture.id).count(), 2)
        self.assertEqual(PageText.objects.for_user(other).count(), 0)
        self.assertEqual(PageText.objects.for_user(AnonymousUser()).count(), 0)
        for user, lecture_id in ((other, lecture.id), (self.user, lecture.id + 1000)):
            with self.assertRaises(Http404) as caught:
                services.get_page_texts(user, lecture_id)
            self.assertEqual(str(caught.exception), "")

    def test_sm8_logged_out_visitor_is_redirected_to_login(self):
        self.client.logout()
        for method in (self.client.get, self.client.post):
            response = method(reverse("upload"))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response["Location"].startswith("/accounts/login/"))
