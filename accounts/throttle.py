"""Login-failure limit: 5 failures per 15 minutes per email and address (AD-7, story 1.2 AC 5).

The failure times are kept in Django's database-backed cache. The key is a hash of the email
and the address, so an email that has no account is limited in exactly the same way.
Known limit: the check and the count are separate steps, so two failures at the same moment
could let one extra try through. Accepted for a local single-user app.
"""

import hashlib
import time

from django.conf import settings
from django.core.cache import cache

from .managers import normalise_email

BLOCKED_MESSAGE = "Too many failed log-in attempts. Try again in 15 minutes."


def now():
    """The clock. Tests replace this one function to move time."""
    return time.time()


def client_address(request):
    # REMOTE_ADDR only: X-Forwarded-For can be written by the visitor.
    return request.META.get("REMOTE_ADDR", "")


def _key(email, address):
    raw = f"{normalise_email(email)}|{address}"
    return "loginfail:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _recent_failures(key):
    cutoff = now() - settings.LOGIN_FAILURE_WINDOW_SECONDS
    return [t for t in cache.get(key, []) if t > cutoff]


def is_blocked(email, address):
    return len(_recent_failures(_key(email, address))) >= settings.LOGIN_FAILURE_LIMIT


def record_failure(email, address):
    key = _key(email, address)
    times = _recent_failures(key) + [now()]
    cache.set(key, times, timeout=settings.LOGIN_FAILURE_WINDOW_SECONDS + 60)


def clear(email, address):
    cache.delete(_key(email, address))
