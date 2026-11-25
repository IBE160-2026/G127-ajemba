"""Tests for core/ai_client.py (story 3.1). No key, no network: a fake transport stands in (AD-14)."""

from datetime import timedelta
from unittest import mock

from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from accounts.tests import make_user
from config.settings import _usable_gemini_key
from core import ai_client
from core.ai_client import AiCallFailed, AiReplayMissing, RawAnswer
from lectures.models import AiCallLog, RateLimitState

FAKE_KEY = "fake-test-key-not-real-0123456789"
GOOD = RawAnswer(text='{"ok": true}', input_tokens=10, output_tokens=5)


class FakeError(Exception):
    """Looks like the provider's error: a code and a message that could echo request details."""

    def __init__(self, code, message=""):
        super().__init__(f"{code} {message} key={FAKE_KEY}")
        self.code = code
        self.message = message


def failing(*errors):
    """A transport that raises each error in turn, then answers."""
    queue = list(errors)
    calls = []

    def transport(model, prompt, schema, timeout):
        calls.append(timeout)
        if queue:
            raise queue.pop(0)
        return GOOD

    transport.calls = calls
    return transport


class KeyDetectionTests(SimpleTestCase):
    def test_missing_keys_count_as_missing(self):
        """AD-12.2: empty, spaces, placeholder and wrong shape give no key."""
        for raw in ["", "   ", "your_key_here", "changeme", "paste-your-key", "short", "has space in it 1234567890", None]:
            self.assertEqual(_usable_gemini_key(raw), "", repr(raw))

    def test_key_with_dots_and_a_word_inside_counts(self):
        """A real key is random: a dot, or 'your' inside it, must not turn it into Demo Mode."""
        self.assertEqual(_usable_gemini_key("AQ.Ab8RN6yourX0123456789abcdefghij"), "AQ.Ab8RN6yourX0123456789abcdefghij")

    def test_real_google_key_shape_counts(self):
        """A key of the real shape (4-letter prefix + 35 URL-safe characters) is accepted.

        Built here from pieces, so no file contains a string that looks like a real key.
        """
        real_shape = "AI" + "za" + "x" * 35
        self.assertEqual(len(real_shape), 39)
        self.assertEqual(_usable_gemini_key(real_shape), real_shape)

    def test_plausible_key_counts(self):
        self.assertEqual(_usable_gemini_key(f"  {FAKE_KEY} "), FAKE_KEY)

    @override_settings(GEMINI_API_KEY="", GEMINI_KEY_PRESENT=False)
    def test_no_key_means_replay_and_no_client(self):
        self.assertFalse(ai_client.key_present())
        with mock.patch.object(ai_client, "_genai_transport", side_effect=AssertionError("client built")):
            self.assertEqual(ai_client.call("summary", "sample-1")["parts"][0]["slides"], [1, 2])


class RetryWaitsSettingTests(SimpleTestCase):
    def test_retry_waits_parse_and_refuse_bad_values(self):
        from django.core.exceptions import ImproperlyConfigured

        from config.settings import _retry_waits

        self.assertEqual(_retry_waits("2,5,10"), (2, 5, 10))
        self.assertEqual(_retry_waits(" 1 , 3 "), (1, 3))
        for bad in ["", "a,b", "2,,5", "-1", "61", "1,2,3,4,5,6"]:
            with self.assertRaises(ImproperlyConfigured, msg=bad):
                _retry_waits(bad)


class ReplayTests(SimpleTestCase):
    def test_replay_hit(self):
        self.assertIn("key_terms", ai_client.replay("summary", "sample-1")["parts"][0])

    def test_replay_miss_is_clear_error(self):
        with self.assertRaises(AiReplayMissing):
            ai_client.replay("summary", "does-not-exist")

    @override_settings(GEMINI_API_KEY=FAKE_KEY, GEMINI_KEY_PRESENT=True)
    def test_example_never_reaches_the_provider(self):
        """AD-10.2: an example lecture is replayed even when a key exists."""
        with mock.patch.object(ai_client, "_genai_transport", side_effect=AssertionError("called")):
            ai_client.call("summary", "sample-1", is_example=True)


@override_settings(GEMINI_API_KEY=FAKE_KEY, GEMINI_KEY_PRESENT=True, AI_RETRY_WAITS_S=(2, 5, 10))
class RealCallTests(TestCase):
    def setUp(self):
        self.user = make_user()
        patcher = mock.patch.object(ai_client, "_sleep")
        self.sleep = patcher.start()
        self.addCleanup(patcher.stop)

    def run_call(self, transport, **kw):
        return ai_client.call("summary", 1, user=self.user, prompt="text", transport=transport, **kw)

    def test_success_logs_one_row_without_content(self):
        self.assertEqual(self.run_call(failing(), prompt_version="v1"), {"ok": True})
        row = AiCallLog.objects.get()
        self.assertEqual((row.task, row.input_tokens, row.output_tokens, row.prompt_version), ("summary", 10, 5, "v1"))
        self.assertIsNotNone(row.local_day)

    def test_503_three_retries_with_growing_waits_then_calm_error(self):
        transport = failing(*[FakeError(503)] * 4)
        with self.assertRaises(AiCallFailed) as ctx:
            self.run_call(transport)
        self.assertEqual(len(transport.calls), 4)
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [2, 5, 10])
        self.assertEqual(str(ctx.exception), ai_client.MSG_FAILED)
        self.assertNotIn(FAKE_KEY, str(ctx.exception))
        self.assertEqual(AiCallLog.objects.count(), 4)

    def test_three_503_then_success(self):
        transport = failing(*[FakeError(503)] * 3)
        self.assertEqual(self.run_call(transport), {"ok": True})
        self.assertEqual(len(transport.calls), 4)
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [2, 5, 10])

    def test_429_and_503_can_be_mixed(self):
        transport = failing(FakeError(429, "slow down"), FakeError(503))
        self.assertEqual(self.run_call(transport), {"ok": True})
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [2, 5])

    def test_quota_zero_on_a_later_error_stops_at_once(self):
        transport = failing(FakeError(503), FakeError(429, "quota exceeded, limit: 0"))
        with self.assertRaises(AiCallFailed) as ctx:
            self.run_call(transport)
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [2])
        self.assertEqual(ctx.exception.reason, "quota_zero")

    def test_a_wait_that_does_not_fit_the_job_budget_fails_without_sleeping(self):
        transport = failing(*[FakeError(503)] * 4)
        with self.assertRaises(AiCallFailed) as ctx:
            self.run_call(transport, budget=ai_client.JobBudget(4))
        self.assertEqual(ctx.exception.reason, "job_budget")
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [2])
        self.assertEqual(len(transport.calls), 2)

    def test_429_retry_then_success(self):
        transport = failing(FakeError(429, "slow down"))
        self.assertEqual(self.run_call(transport), {"ok": True})
        self.assertEqual(len(transport.calls), 2)

    def test_429_four_times_gives_calm_error_without_key(self):
        with self.assertLogs("recall.ai", level="INFO") as logs, self.assertRaises(AiCallFailed) as ctx:
            self.run_call(failing(*[FakeError(429)] * 4))
        self.assertNotIn(FAKE_KEY, str(ctx.exception))
        self.assertIsNone(ctx.exception.__cause__)
        self.assertNotIn(FAKE_KEY, " ".join(r.getMessage() for r in logs.records))

    def test_quota_zero_is_not_retried(self):
        transport = failing(FakeError(429, "quota exceeded, limit: 0"))
        with self.assertRaises(AiCallFailed) as ctx:
            self.run_call(transport)
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(ctx.exception.reason, "quota_zero")
        self.assertEqual(str(ctx.exception), ai_client.MSG_FAILED)

    def test_other_error_not_retried(self):
        transport = failing(FakeError(400))
        with self.assertRaises(AiCallFailed):
            self.run_call(transport)
        self.assertEqual(len(transport.calls), 1)

    def test_timeout_fails_calmly(self):
        class ReadTimeout(Exception):
            pass

        with self.assertRaises(AiCallFailed) as ctx:
            self.run_call(failing(ReadTimeout("slow")))
        self.assertEqual(ctx.exception.reason, "timeout")

    @override_settings(MAX_PROMPT_CHARS=10)
    def test_prompt_over_limit_refused_before_any_call(self):
        transport = failing()
        with self.assertRaises(AiCallFailed):
            ai_client.call("summary", 1, user=self.user, prompt="x" * 11, transport=transport)
        self.assertEqual(transport.calls, [])

    def test_job_budget_used_up_fails(self):
        with self.assertRaises(AiCallFailed) as ctx:
            self.run_call(failing(), budget=ai_client.JobBudget(0))
        self.assertEqual(ctx.exception.reason, "job_budget")

    def test_timeout_is_capped_by_remaining_budget(self):
        transport = failing()
        self.run_call(transport, budget=ai_client.JobBudget(20))
        self.assertLessEqual(transport.calls[0], 20)

    @override_settings(AI_REQUESTS_PER_MINUTE=2, RATE_WAIT_MAX_S=90)
    def test_rate_row_makes_third_call_wait(self):
        for _ in range(3):
            self.run_call(failing())
        self.assertEqual(RateLimitState.objects.get().day_count, 3)
        self.assertTrue(self.sleep.called)
        self.assertLessEqual(self.sleep.call_args[0][0], 60)

    @override_settings(AI_REQUESTS_PER_MINUTE=1, RATE_WAIT_MAX_S=5)
    def test_wait_over_rate_wait_max_fails(self):
        self.run_call(failing())
        with self.assertRaises(AiCallFailed) as ctx:
            self.run_call(failing())
        self.assertEqual(ctx.exception.reason, "rate_wait_too_long")

    @override_settings(AI_REQUESTS_PER_DAY=1)
    def test_day_limit_fails(self):
        self.run_call(failing())
        with self.assertRaises(AiCallFailed) as ctx:
            self.run_call(failing())
        self.assertEqual(ctx.exception.reason, "day_limit")

    def test_new_minute_window_resets_count(self):
        RateLimitState.objects.create(pk=1, minute_start=timezone.now() - timedelta(seconds=120), minute_count=99)
        self.run_call(failing())
        self.assertEqual(RateLimitState.objects.get().minute_count, 1)
        self.sleep.assert_not_called()


class RateWindowTests(TestCase):
    @override_settings(AI_REQUESTS_PER_MINUTE=1, RATE_WAIT_MAX_S=90)
    def test_second_caller_in_a_full_minute_also_waits(self):
        """The window is moved to the future when the minute is full; a later caller must wait for it too."""
        now = timezone.now()
        ai_client._reserve_slot(now)
        first = ai_client._reserve_slot(now)
        second = ai_client._reserve_slot(now)
        self.assertGreater(first, 0)
        self.assertGreaterEqual(second, first)


class StartWithoutKeyTests(SimpleTestCase):
    """AD-12.2: the app starts with a copied .env.example and with a hostile GEMINI_API_KEY, in Demo Mode."""

    def _present_in_child(self, extra_env):
        import os
        import shutil
        import subprocess
        import sys
        import tempfile
        from pathlib import Path

        base = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / ".env"
            shutil.copy(base / ".env.example", copied)
            env = {**os.environ, "RECALL_ENV_FILE": str(copied), "DJANGO_SETTINGS_MODULE": "config.settings", **extra_env}
            code = "from django.conf import settings; print(settings.GEMINI_KEY_PRESENT)"
            out = subprocess.run([sys.executable, "-c", code], cwd=base, env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr[-300:])
        return out.stdout.strip()

    def test_copied_env_example_means_no_key(self):
        self.assertEqual(self._present_in_child({"GEMINI_API_KEY": ""}), "False")

    def test_hostile_values_mean_no_key(self):
        for hostile in ("   ", "your_key_here", "<script>alert(1)</script>-0123456789"):
            self.assertEqual(self._present_in_child({"GEMINI_API_KEY": hostile}), "False", hostile)
