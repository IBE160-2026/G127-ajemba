"""Story 3.2: background jobs, the Processing page, the lecture list and retry (FR-5, AD-3, AD-11, AD-23)."""

import os
import shutil
import traceback
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import timedelta
from pathlib import Path
from unittest import mock

from django.conf import settings as django_settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.tests import STRONG_PASSWORD, make_user
from core import jobs

from . import services
from .models import AiCallLog, Lecture, PageText
from .tests import GOOD_LINE, mask_tokens, pdf_bytes, upload_file

BASE_DIR = Path(django_settings.BASE_DIR)


def make_lecture(user, title="Networks", status=Lecture.PROCESSING, minutes_old=0, retry_count=0):
    lecture = Lecture.objects.create(user=user, title=title, status=status, retry_count=retry_count)
    Lecture.objects.filter(pk=lecture.pk).update(status_changed_at=timezone.now() - timedelta(minutes=minutes_old))
    lecture.refresh_from_db()
    return lecture


class Base(TestCase):
    def setUp(self):
        # Jobs run here on lectures with no page text, but no test may ever reach the provider.
        refuse = mock.Mock(side_effect=AssertionError("a test tried a real provider call"))
        patcher = mock.patch("core.ai_client._genai_transport", refuse)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.user = make_user("a@example.com")
        self.other = make_user("b@example.com")
        self.client.login(email="a@example.com", password=STRONG_PASSWORD)


class SetStatusAndJobTests(Base):
    def test_fr5_job_runs_once_when_enqueued_twice(self):
        """AC 2: only the first run changes the status; the second stops without work."""
        lecture = make_lecture(self.user)
        self.assertTrue(services.set_status(lecture, [Lecture.PROCESSING], Lecture.FAILED))
        changed_at = Lecture.objects.get(pk=lecture.pk).status_changed_at
        again = Lecture.objects.get(pk=lecture.pk)
        self.assertFalse(services.set_status(again, [Lecture.PROCESSING], Lecture.FAILED))
        self.assertEqual(Lecture.objects.get(pk=lecture.pk).status_changed_at, changed_at)

        second = make_lecture(self.user, "Second")
        jobs.run_job(jobs.SUMMARY, second.id)
        stamp = Lecture.objects.get(pk=second.pk).status_changed_at
        jobs.run_job(jobs.SUMMARY, second.id)  # the same id enqueued twice
        after = Lecture.objects.get(pk=second.pk)
        self.assertEqual((after.status, after.status_changed_at), (Lecture.FAILED, stamp))

    def test_set_status_refuses_an_edge_that_is_not_allowed(self):
        lecture = make_lecture(self.user, status=Lecture.FAILED)
        with self.assertRaises(ValueError):
            services.set_status(lecture, [Lecture.FAILED], Lecture.READY)

    def test_job_for_a_deleted_lecture_does_nothing(self):
        lecture = make_lecture(self.user)
        lecture_id = lecture.id
        lecture.delete()
        jobs.run_job(jobs.SUMMARY, lecture_id)  # no error

    def test_job_arguments_are_ids_only(self):
        """AC 3: an integer id goes in, no text; the queue write waits for the commit."""
        lecture = make_lecture(self.user)
        PageText.objects.create(lecture=lecture, number=1, text="Secret slide text")
        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            jobs.enqueue(jobs.SUMMARY, lecture.id)
            self.assertEqual(jobs.queued_arguments(), [], "queued before the commit")
        self.assertEqual(len(callbacks), 1)
        callbacks[0]()
        queued = jobs.queued_arguments()
        self.assertEqual(queued, [("core.jobs.run_job", (jobs.SUMMARY, lecture.id))])
        self.assertIsInstance(queued[0][1][1], int)
        for bad in ("Secret slide text", 1.5, True, None):
            with self.assertRaises(TypeError):
                jobs.enqueue(jobs.SUMMARY, bad)
        with self.assertRaises(ValueError):
            jobs.enqueue("unknown", 1)
        self.assertEqual(jobs.run_job(jobs.SUMMARY, "5"), None)  # a text id is refused, nothing runs

    def test_upload_queues_the_job_with_the_lecture_id(self):
        services.acknowledge_notice(self.user)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("upload"), {"pdf": upload_file(pdf_bytes([GOOD_LINE, GOOD_LINE]), "slides.pdf")}
            )
        lecture = Lecture.objects.get()
        self.assertRedirects(response, reverse("lecture_detail", args=[lecture.id]))
        self.assertEqual(jobs.queued_arguments(), [("core.jobs.run_job", (jobs.SUMMARY, lecture.id))])


class FailedJobStoresNoTextTests(Base):
    def test_ad3_failed_job_result_holds_the_class_name_and_no_slide_text(self):
        """django-q2 stores a failed task as f"{error} : {traceback}" (worker.py) and never prunes it.
        A job that fails with slide text in its message must leave no text in that string."""
        lecture = make_lecture(self.user)
        PageText.objects.create(lecture=lecture, number=1, text="Secret slide text about quantum cheese")

        def broken_job(lecture_id):
            text = PageText.objects.get(lecture_id=lecture_id).text
            raise ValueError(f"bad answer for: {text}")

        with mock.patch.dict(jobs.JOBS, {jobs.SUMMARY: broken_job}):
            with self.assertLogs("recall.jobs", level="ERROR") as logged:
                with self.assertRaises(jobs.JobFailed) as caught:
                    jobs.run_job(jobs.SUMMARY, lecture.id)
        # What the worker would store, with the whole traceback (original and chained errors).
        stored = f"{caught.exception} : " + "".join(traceback.format_exception(caught.exception))
        self.assertIn("ValueError", stored)
        self.assertIn("JobFailed", stored)  # the traceback really is in the string being checked
        self.assertNotIn("quantum", stored)
        self.assertNotIn("bad answer", stored)
        self.assertNotIn("quantum", "".join(logged.output))


class StaleTests(Base):
    def test_fr5_stale_processing_becomes_failed(self):
        """AC 4: reaped when the status view is read, and by the command run.py calls."""
        stale = make_lecture(self.user, "Stale", minutes_old=11)
        fresh = make_lecture(self.user, "Fresh", minutes_old=2)
        response = self.client.get(reverse("lecture_status", args=[stale.id]), HTTP_HX_REQUEST="true")
        self.assertContains(response, "Try again")
        self.assertEqual(Lecture.objects.get(pk=stale.pk).status, Lecture.FAILED)
        self.assertEqual(Lecture.objects.get(pk=fresh.pk).status, Lecture.PROCESSING)

    def test_fr5_reap_command_marks_stale_lectures(self):
        from django.core.management import call_command

        stale = make_lecture(self.user, minutes_old=30)
        call_command("reap_stale", stdout=mock.MagicMock())
        self.assertEqual(Lecture.objects.get(pk=stale.pk).status, Lecture.FAILED)


class RetryTests(Base):
    def test_fr5_retry_limited_to_three(self):
        """AC 5: three retries go back to processing; the fourth is refused with a plain message."""
        lecture = make_lecture(self.user, status=Lecture.FAILED)
        url = reverse("lecture_retry", args=[lecture.id])
        for attempt in (1, 2, 3):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(url)
            self.assertRedirects(response, reverse("lecture_detail", args=[lecture.id]))
            lecture.refresh_from_db()
            self.assertEqual((lecture.status, lecture.retry_count), (Lecture.PROCESSING, attempt))
            services.set_status(lecture, [Lecture.PROCESSING], Lecture.FAILED)
        self.assertEqual(len(jobs.queued_arguments()), 3)
        response = self.client.post(url)
        self.assertContains(response, services.MSG_RETRY_LIMIT, status_code=400)
        lecture.refresh_from_db()
        self.assertEqual((lecture.status, lecture.retry_count), (Lecture.FAILED, 3))
        self.assertEqual(len(jobs.queued_arguments()), 3)

    def test_retry_adds_no_upload_row_and_needs_a_failed_lecture(self):
        lecture = make_lecture(self.user, status=Lecture.PROCESSING)
        response = self.client.post(reverse("lecture_retry", args=[lecture.id]))
        self.assertContains(response, services.MSG_RETRY_NOT_FAILED, status_code=400)
        self.assertEqual(services.UploadLog.objects.count(), 0)

    def test_retry_is_post_only_and_owner_scoped(self):
        lecture = make_lecture(self.user, status=Lecture.FAILED)
        url = reverse("lecture_retry", args=[lecture.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.logout()
        self.client.login(email="b@example.com", password=STRONG_PASSWORD)
        missing = self.client.get(reverse("lecture_retry", args=[999999]))
        for method in ("get", "post"):
            response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(mask_tokens(response.content.decode()), mask_tokens(missing.content.decode()))
        lecture.refresh_from_db()
        self.assertEqual((lecture.status, lecture.retry_count), (Lecture.FAILED, 0))


class PagesTests(Base):
    def test_fr5_processing_page_is_honest(self):
        """AC 6: two real steps, no percentage, no timer, polls every 3 seconds."""
        lecture = make_lecture(self.user)
        html = self.client.get(reverse("lecture_detail", args=[lecture.id])).content.decode()
        self.assertIn("Reading your PDF: Done", html)
        self.assertIn("Writing the summary: In progress", html)
        self.assertIn(f'hx-get="/status/lecture/{lecture.id}/"', html)
        self.assertIn('hx-trigger="every 3s"', html)
        self.assertNotIn("%", html)
        self.assertNotIn("progress", html.replace("In progress", ""))

    def test_fr5_polling_stops_at_ready_and_failed(self):
        for status in (Lecture.READY, Lecture.FAILED):
            lecture = make_lecture(self.user, status=status)
            response = self.client.get(reverse("lecture_status", args=[lecture.id]), HTTP_HX_REQUEST="true")
            self.assertNotContains(response, "hx-trigger")
            self.assertNotContains(response, "<html")  # a partial, not a full page

    def test_status_view_without_htmx_is_a_full_page(self):
        lecture = make_lecture(self.user)
        self.assertContains(self.client.get(reverse("lecture_status", args=[lecture.id])), "<html")

    def test_status_view_other_user_gets_404(self):
        """AC 6 and AD-8.2: a wrong owner and a missing id look the same."""
        lecture = make_lecture(self.user, "Private Title")
        self.client.logout()
        self.client.login(email="b@example.com", password=STRONG_PASSWORD)
        wrong = self.client.get(reverse("lecture_status", args=[lecture.id]), HTTP_HX_REQUEST="true")
        missing = self.client.get(reverse("lecture_status", args=[999999]), HTTP_HX_REQUEST="true")
        self.assertEqual((wrong.status_code, missing.status_code), (404, 404))
        self.assertEqual(mask_tokens(wrong.content.decode()), mask_tokens(missing.content.decode()))
        self.assertNotContains(wrong, "Private Title", status_code=404)

    def test_status_view_logged_out_goes_to_login(self):
        lecture = make_lecture(self.user)
        self.client.logout()
        response = self.client.get(reverse("lecture_status", args=[lecture.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_fr5_list_shows_real_status_of_own_lectures_only(self):
        """AC 7."""
        make_lecture(self.user, "Own processing")
        make_lecture(self.user, "Own ready", status=Lecture.READY)
        failed = make_lecture(self.user, "Own failed", status=Lecture.FAILED)
        make_lecture(self.other, "Someone else's lecture")
        html = self.client.get(reverse("lectures")).content.decode()
        self.assertIn("Status: Processing", html)
        self.assertIn("Status: Ready", html)
        self.assertIn("Status: Failed", html)
        self.assertIn(f'action="{reverse("lecture_retry", args=[failed.id])}"', html)
        self.assertIn("Try again", html)
        self.assertNotIn("Someone else", html)


@override_settings(AI_CALLS_PER_USER_PER_DAY=2, AI_CALLS_GLOBAL_PER_DAY=3)
class AiBudgetTests(Base):
    def log_calls(self, user, count):
        for _ in range(count):
            AiCallLog.objects.create(user=user, task="summary", local_day=services.local_today())

    def test_ad23_job_not_queued_when_ai_budget_used_up(self):
        """AC 9: per-user budget and global ceiling, for a new upload and for a retry."""
        services.acknowledge_notice(self.user)
        self.log_calls(self.user, 2)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("upload"), {"pdf": upload_file(pdf_bytes([GOOD_LINE, GOOD_LINE]), "slides.pdf")}
            )
        self.assertContains(response, services.MSG_AI_BUDGET, status_code=400)
        self.assertEqual((Lecture.objects.count(), services.UploadLog.objects.count()), (0, 0))
        self.assertEqual(jobs.queued_arguments(), [])

        failed = make_lecture(self.user, status=Lecture.FAILED)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("lecture_retry", args=[failed.id]))
        self.assertContains(response, services.MSG_AI_BUDGET, status_code=400)
        failed.refresh_from_db()
        self.assertEqual((failed.status, failed.retry_count), (Lecture.FAILED, 0))
        self.assertEqual(jobs.queued_arguments(), [])

    def test_ad23_global_ceiling_stops_everybody(self):
        self.log_calls(self.other, 2)
        self.log_calls(self.user, 1)  # the user is under their own 2, but 3 calls were made today
        self.assertFalse(services.ai_budget_left(self.user))
        self.assertFalse(services.ai_budget_left(self.other))

    def test_ad23_yesterdays_calls_do_not_count(self):
        AiCallLog.objects.create(
            user=self.user, task="summary", local_day=services.local_today() - timedelta(days=1)
        )
        self.log_calls(self.user, 1)
        self.assertTrue(services.ai_budget_left(self.user))

    def test_ai_call_log_is_owner_scoped(self):
        self.log_calls(self.user, 1)
        self.assertEqual(AiCallLog.objects.for_user(self.user).count(), 1)
        self.assertEqual(AiCallLog.objects.for_user(self.other).count(), 0)
        self.assertEqual(AiCallLog.objects.for_user(None).count(), 0)


class RealWorkerTests(SimpleTestCase):
    """AC 1 and AC 8: a real django-q2 worker, started on its own, finishes a job with no web page open."""

    def test_fr5_job_finishes_after_page_closed(self):
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder, True)
        db_file = str(Path(folder) / "worker.sqlite3")
        env = {**os.environ, "DATABASE_FILE": db_file, "RECALL_ENV_FILE": str(BASE_DIR / "no-such-env-file")}
        for name in ("RECALL_ENV", "SECRET_KEY"):
            env.pop(name, None)
        run = lambda *args: subprocess.run([sys.executable, *args], cwd=BASE_DIR, env=env, check=True)
        run("manage.py", "migrate", "-v", "0")
        # "The user uploads and closes the page": a lecture exists and its job is queued; no web server runs.
        run("-c", (
            "import django, os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings'; django.setup();"
            "from django.contrib.auth import get_user_model; from lectures.models import Lecture; from core import jobs;"
            "u=get_user_model().objects.create_user(email='w@example.com', password='x'*20);"
            "l=Lecture.objects.create(user=u, title='T'); jobs.enqueue('summary', l.id); jobs.enqueue('summary', l.id)"
        ))
        worker = subprocess.Popen(
            [sys.executable, "manage.py", "qcluster"], cwd=BASE_DIR, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

        def stop_worker():
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(worker.pid)], capture_output=True)
            else:
                worker.kill()
            worker.wait(timeout=10)

        self.addCleanup(stop_worker)

        def read(sql):
            with sqlite3.connect(db_file, timeout=10) as db:
                return db.execute(sql).fetchall()

        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if read("select status from lectures_lecture") == [("failed",)] and not read("select id from django_q_ormq"):
                break
            time.sleep(0.5)
        self.assertEqual(read("select status, retry_count from lectures_lecture"), [("failed", 0)])
        self.assertEqual(read("select id from django_q_ormq"), [], "the queue was not emptied")
        # Successful tasks are not stored (save_limit -1). Failed ones would be; see FailedJobStoresNoTextTests.
        self.assertEqual(read("select id from django_q_task where success = 1"), [])
