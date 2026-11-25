"""The only module that talks to the AI provider (AD-4). Nothing else names it or imports its library.

`call(task, id, ...)` runs in a job, never in a web request. With a usable key and a real lecture it
makes one real call (bounded, rate limited, logged). Otherwise it replays a stored answer keyed by
(task, id). The key comes only from settings; it is never logged, printed or put in an error text.
No lecture text goes into the AiCallLog row or the logs. Prompts and validators are story 3.3.
"""

import json
import logging
import re
import secrets
import time
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .validation import ValidationFailed, validate_summary

logger = logging.getLogger("recall.ai")

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_responses"
PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

# A bad answer is retried at most twice per logical call, shared by structure and grounding failures
# (AD-4.4, FR-27). That is at most three requests for one Summary.
VALIDATION_RETRIES = 2

# The plain message of FR-5. The job shows this to the student; it never holds details or the key.
MSG_FAILED = "We could not make this right now. Please try again in a few minutes."
MSG_TOO_LONG = "This lecture has too much text for one request. Please choose a shorter PDF."


class AiError(Exception):
    """Base class. The text is always safe to show: no key, no lecture text."""


class AiReplayMissing(AiError):
    """Replay mode has no stored answer for this (task, id)."""


class AiCallFailed(AiError):
    """A real call failed or hit a bound. `reason` is a short code for logs; `str()` is the FR-5 message."""

    def __init__(self, message=MSG_FAILED, reason="failed"):
        super().__init__(message)
        self.reason = reason


class AiNotJson(AiCallFailed):
    """The answer was not JSON. A wrong structure like any other, so the retry loop may try again."""


@dataclass
class RawAnswer:
    """What a transport returns: the answer text and approximate token counts."""

    text: str
    input_tokens: int = 0
    output_tokens: int = 0


class JobBudget:
    """Total time one job may spend in AI calls, waiting included (AI_JOB_BUDGET_S)."""

    def __init__(self, seconds=None):
        self.seconds = settings.AI_JOB_BUDGET_S if seconds is None else seconds
        self.started = time.monotonic()

    def remaining(self):
        return self.seconds - (time.monotonic() - self.started)


def key_present():
    """True only if settings found a usable key (not empty, not a placeholder, plausible shape)."""
    return bool(settings.GEMINI_KEY_PRESENT and settings.GEMINI_API_KEY)


def _sleep(seconds):
    time.sleep(seconds)


# --- Replay ----------------------------------------------------------------------------------

def _safe_part(value):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in str(value))


def replay(task, id):
    """Return the stored answer for (task, id), or raise AiReplayMissing. No network, no key."""
    path = SAMPLE_DIR / f"{_safe_part(task)}__{_safe_part(id)}.json"
    if not path.is_file():
        raise AiReplayMissing(f"No stored sample answer for task '{task}' and id '{id}'.")
    return json.loads(path.read_text(encoding="utf-8"))


# --- Shared rate row (AD-4.6) ----------------------------------------------------------------

def _reserve_slot(now=None):
    """Count one request against the minute and day limits in one short transaction.

    Returns the seconds to wait before sending (0 if free). Raises AiCallFailed when the day is
    used up. The wait is served by the caller outside the transaction.
    """
    from lectures.models import RateLimitState
    from lectures.services import local_today

    now = now or timezone.now()
    with transaction.atomic():
        row, _ = RateLimitState.objects.get_or_create(pk=1, defaults={"minute_start": now})
        today = local_today()
        if row.local_day != today:
            row.local_day, row.day_count = today, 0
        if row.day_count >= settings.AI_REQUESTS_PER_DAY:
            raise AiCallFailed(reason="day_limit")
        window_end = row.minute_start + timedelta(seconds=60)
        wait = 0.0
        if now >= window_end:
            row.minute_start, row.minute_count = now, 0
        elif row.minute_start > now:
            # A full minute already moved the window into the future: every caller waits for its start.
            wait = (row.minute_start - now).total_seconds()
            if wait > settings.RATE_WAIT_MAX_S:
                raise AiCallFailed(reason="rate_wait_too_long")
        elif row.minute_count >= settings.AI_REQUESTS_PER_MINUTE:
            wait = (window_end - now).total_seconds()
            if wait > settings.RATE_WAIT_MAX_S:
                raise AiCallFailed(reason="rate_wait_too_long")
            # The slot belongs to the next window: start it when the wait is over.
            row.minute_start, row.minute_count = window_end, 0
        row.minute_count += 1
        row.day_count += 1
        row.save()
    return wait


# --- Real call -------------------------------------------------------------------------------

def _genai_transport(model, prompt, schema, timeout_s):
    """The one place the provider library is used. The key is passed explicitly (AD-4.1)."""
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=int(timeout_s * 1000)),
    )
    config = {"response_mime_type": "application/json"}
    if schema is not None:
        config["response_json_schema"] = schema
    response = client.models.generate_content(
        model=model, contents=prompt, config=types.GenerateContentConfig(**config)
    )
    usage = response.usage_metadata
    return RawAnswer(
        text=response.text or "",
        input_tokens=getattr(usage, "prompt_token_count", 0) or 0,
        output_tokens=getattr(usage, "candidates_token_count", 0) or 0,
    )


def _error_code(error):
    code = getattr(error, "code", None) or getattr(error, "status_code", None)
    return code if isinstance(code, int) else None


def _is_timeout(error):
    return "timeout" in type(error).__name__.lower() or isinstance(error, TimeoutError)


def _quota_zero(error):
    """Free quota for this model is zero: retrying cannot help (AD-4.5)."""
    text = f"{getattr(error, 'message', '')} {error}".lower()
    return "limit: 0" in text


def _log_call(user, task, model, prompt_version, answer, elapsed):
    from lectures.models import AiCallLog
    from lectures.services import local_today

    AiCallLog.objects.create(
        user=user,
        task=task,
        model=model,
        prompt_version=prompt_version,
        input_tokens=answer.input_tokens if answer else 0,
        output_tokens=answer.output_tokens if answer else 0,
        wait_seconds=round(elapsed, 2),
        local_day=local_today(),
    )


def _attempt(user, task, prompt_version, prompt, schema, budget, transport):
    """One bounded real request: reserve a slot, wait if needed, send, log one row."""
    wait = _reserve_slot()
    if wait:
        if wait > budget.remaining():
            raise AiCallFailed(reason="job_budget")
        _sleep(wait)
    timeout = min(settings.AI_CALL_TIMEOUT_S, budget.remaining())
    if timeout <= 0:
        raise AiCallFailed(reason="job_budget")
    started = time.monotonic()
    answer = None
    try:
        answer = transport(settings.GEMINI_MODEL, prompt, schema, timeout)
        return answer
    finally:
        _log_call(user, task, settings.GEMINI_MODEL, prompt_version, answer, time.monotonic() - started)


def call(task, id, *, user=None, prompt="", schema=None, prompt_version="", is_example=False,
         budget=None, transport=None):
    """Return the parsed JSON answer (a dict) for one task.

    Replays a stored answer when there is no usable key or the object is an example (AD-10.2).
    Raises AiReplayMissing (replay) or AiCallFailed (real call); both texts are safe to show.
    `transport` is for tests: a function (model, prompt, schema, timeout_s) -> RawAnswer.
    """
    # A fake transport (tests only) stands in for the key; the real transport needs a usable key.
    if is_example or (transport is None and not key_present()):
        return replay(task, id)
    if len(prompt) > settings.MAX_PROMPT_CHARS:
        raise AiCallFailed(MSG_TOO_LONG, reason="too_long")
    if user is None:
        raise AiCallFailed(reason="no_user")

    budget = budget or JobBudget()
    transport = transport or _genai_transport
    retried = False
    while True:
        try:
            answer = _attempt(user, task, prompt_version, prompt, schema, budget, transport)
            return json.loads(answer.text)
        except AiCallFailed:
            raise
        except json.JSONDecodeError:
            logger.warning("ai task=%s id=%s result=failed reason=not_json", task, id)
            raise AiNotJson(reason="not_json") from None
        except Exception as error:  # class name and code only: the text could echo request details
            code = _error_code(error)
            reason = f"{type(error).__name__}:{code or '-'}"
            if _is_timeout(error):
                logger.warning("ai task=%s id=%s result=failed reason=%s", task, id, reason)
                raise AiCallFailed(reason="timeout") from None
            busy = code in (503, 429) and not _quota_zero(error)
            if not busy or retried:
                logger.warning("ai task=%s id=%s result=failed reason=%s", task, id, reason)
                raise AiCallFailed(reason="quota_zero" if _quota_zero(error) else reason) from None
            retried = True
            if settings.AI_RETRY_WAIT_S > budget.remaining():
                raise AiCallFailed(reason="job_budget") from None
            logger.info("ai task=%s id=%s busy=%s retry=1", task, id, code)
            _sleep(settings.AI_RETRY_WAIT_S)


# --- The Summary task (AD-4.4, AD-5, AD-6) ---------------------------------------------------

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "language": {"type": "string", "enum": ["en", "nb"]},
        "parts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "text": {"type": "string"},
                    "slides": {"type": "array", "items": {"type": "integer"}},
                    "key_terms": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {"term": {"type": "string"}, "explanation": {"type": "string"}},
                            "required": ["term", "explanation"],
                        },
                    },
                },
                "required": ["heading", "text", "slides", "key_terms"],
            },
        },
    },
    "required": ["language", "parts"],
}

_HEADER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def load_prompt(name):
    """Return (version, body) of `prompts/<name>.md`. Only this module reads prompt files (AD-6)."""
    raw = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    match = _HEADER.match(raw)
    version = ""
    if match:
        for line in match.group(1).splitlines():
            if line.startswith("version:"):
                version = line.split(":", 1)[1].strip()
        raw = raw[match.end():]
    return version, raw


def neutralise(text):
    """Make `<<` and `>>` impossible in slide text, so a slide cannot forge or close a marker (AD-5.2)."""
    while "<<" in text or ">>" in text:
        text = text.replace("<<", "< <").replace(">>", "> >")
    return text


def build_summary_prompt(pages):
    """Return (prompt, prompt_version, token). Each page sits between markers that carry a token made
    for this call; the prompt says marked text is data. Text over MAX_PROMPT_CHARS is refused."""
    version, body = load_prompt("summary")
    token = secrets.token_hex(4)
    marked = "\n\n".join(
        f"<<S{token}:{number}>>\n{neutralise(text)}\n<<E{token}:{number}>>"
        for number, text in enumerate(pages, start=1)
    )
    body = body.replace("{{TOKEN}}", token)
    prompt = body.replace("{{PAGES}}", marked)  # slide text goes in last: it is never searched for slots
    if len(prompt) > settings.MAX_PROMPT_CHARS:
        raise AiCallFailed(MSG_TOO_LONG, reason="too_long")
    return prompt, version, token


def generate_summary(user, lecture_id, pages, budget=None, transport=None):
    """Return (checked summary, generated_with). Raises AiError; the text is always safe to show.

    One shared `budget` covers every request, retries included. In replay mode the stored answer is
    checked once: repeating it cannot give a different answer, so it is not retried.
    """
    version, _ = load_prompt("summary")
    if transport is None and not key_present():
        answer = replay("summary", lecture_id)
        try:
            return validate_summary(answer, pages), f"replay, summary prompt v{version}"
        except ValidationFailed as failure:
            logger.warning("ai task=summary id=%s result=rejected reason=%s", lecture_id, failure.reason)
            raise AiCallFailed(reason=f"invalid:{failure}") from None

    budget = budget or JobBudget()
    last = "invalid"
    for attempt in range(1 + VALIDATION_RETRIES):
        prompt, version, _ = build_summary_prompt(pages)
        try:
            answer = call("summary", lecture_id, user=user, prompt=prompt, schema=SUMMARY_SCHEMA,
                          prompt_version=version, budget=budget, transport=transport)
            return validate_summary(answer, pages), f"{settings.GEMINI_MODEL}, summary prompt v{version}"
        except AiNotJson:
            last = "not_json"
        except ValidationFailed as failure:
            last = f"invalid:{failure}"  # reason code and part number, no text
        logger.warning("ai task=summary id=%s result=rejected reason=%s attempt=%s", lecture_id, last, attempt + 1)
    raise AiCallFailed(reason=last)
