"""Django settings for Recall. The only module that reads the environment (AD-12)."""

import re
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
# RECALL_ENV_FILE lets a test point at a missing file so a developer's own .env cannot hide a failure.
_env_file = Path(env.str("RECALL_ENV_FILE", default=str(BASE_DIR / ".env")))
if _env_file.is_file():
    environ.Env.read_env(str(_env_file))

# "local" (or unset) means development. Anything else is treated as not local.
RECALL_ENV = env.str("RECALL_ENV", default="local").strip().lower() or "local"
DEBUG = RECALL_ENV == "local"

SECRET_KEY = env.str("SECRET_KEY", default="").strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "recall-local-development-key-not-for-real-use"
    else:
        raise ImproperlyConfigured(
            "SECRET_KEY is missing. RECALL_ENV is not 'local', so the app will not "
            "start with a default key. Set SECRET_KEY in .env or the environment."
        )

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_q",  # the background worker; only core/jobs.py imports it (AD-3)
    "accounts",
    "lectures",
]

# Must be set before the first migration is created (AD-7).
AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.WebSafetyMiddleware",  # CSP header and no-store for logged-in pages (AD-19)
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# SQLite with safe settings (AD-24).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # DATABASE_FILE lets a test run its own worker against a throwaway database.
        "NAME": env.str("DATABASE_FILE", default=str(BASE_DIR / "db.sqlite3")),
        "OPTIONS": {
            "timeout": 20,
            "transaction_mode": "IMMEDIATE",
            "init_command": (
                "PRAGMA journal_mode=WAL;"
                "PRAGMA synchronous=NORMAL;"
                "PRAGMA foreign_keys=ON;"
            ),
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# Login pages (AD-7). A bad or missing "next" goes to the home page.
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# The login-failure counters live in a database-backed cache (AD-7). The table is made
# by "createcachetable" (run.py does it). MAX_ENTRIES is high so that a flood of made-up
# emails cannot push real counters out; entries expire a little after the 15-minute window.
LOGIN_FAILURE_LIMIT = 5
LOGIN_FAILURE_WINDOW_SECONDS = 15 * 60
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "recall_cache",
        "TIMEOUT": LOGIN_FAILURE_WINDOW_SECONDS + 60,
        "OPTIONS": {"MAX_ENTRIES": 10000, "CULL_FREQUENCY": 10},
    }
}

# Logs go to the console and to logs/web.log. Never content, passwords or keys (AD-15).
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "plain"},
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "web.log"),
            "formatter": "plain",
            "encoding": "utf-8",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}

# Upload checks (AD-20, FR-3, FR-4).
UPLOAD_MAX_BYTES = 10 * 1024 * 1024
UPLOAD_MAX_PAGES = 50
UPLOAD_MIN_CHARS_PER_PAGE = 100
PDF_EXTRACT_TIMEOUT_SECONDS = 20
# Non-file request bodies stay small; uploaded files go to a temporary file on disk, not memory.
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
FILE_UPLOAD_HANDLERS = ["lectures.upload_handlers.LimitedTemporaryFileUploadHandler"]
# Where temporary copies of an upload are made. None means the system temp folder.
FILE_UPLOAD_TEMP_DIR = None

# Daily upload limit (FR-7, AD-15.5). The day is the local date in LIMIT_TIME_ZONE.
UPLOADS_PER_DAY = env.int("UPLOADS_PER_DAY", default=5)
LIMIT_TIME_ZONE = env.str("LIMIT_TIME_ZONE", default="Europe/Oslo").strip() or "Europe/Oslo"
if UPLOADS_PER_DAY < 1:
    raise ImproperlyConfigured("UPLOADS_PER_DAY must be 1 or more.")
try:
    from zoneinfo import ZoneInfo

    ZoneInfo(LIMIT_TIME_ZONE)
except Exception:
    raise ImproperlyConfigured(f"LIMIT_TIME_ZONE '{LIMIT_TIME_ZONE}' is not a known time zone name.") from None


# Background jobs and status (AD-3, AD-11, AD-23). Names checked against django-q2 1.11.1.
STALE_MINUTES = 10  # a lecture in "processing" longer than this is treated as failed
POLL_SECONDS = 3  # how often the Processing page asks for the status
RETRY_LIMIT = 3  # retries of a failed lecture
AI_CALLS_PER_USER_PER_DAY = env.int("AI_CALLS_PER_USER_PER_DAY", default=30)
AI_CALLS_GLOBAL_PER_DAY = env.int("AI_CALLS_GLOBAL_PER_DAY", default=200)
if AI_CALLS_PER_USER_PER_DAY < 1 or AI_CALLS_GLOBAL_PER_DAY < 1:
    raise ImproperlyConfigured("AI_CALLS_PER_USER_PER_DAY and AI_CALLS_GLOBAL_PER_DAY must be 1 or more.")

# Exactly one worker. "retry" is larger than "timeout" so a running job is never queued again.
# max_attempts 1 and ack_failures: a failed job is never run again by the queue; a retry is our
# own status change. save_limit -1: successful tasks are not stored. Only ids go in (AD-3.1).
Q_CLUSTER = {
    "name": "recall",
    "orm": "default",
    "workers": 1,
    "timeout": 240,
    "retry": 300,
    "max_attempts": 1,
    "ack_failures": True,
    "save_limit": -1,
    "recycle": 100,
    "poll": 0.5,
    "scheduler": False,
}

# Gemini (AD-4, AD-12). The raw key is read only here and is never logged or printed.
# A key counts as present only if it is not empty, not a placeholder and has a plausible shape;
# otherwise GEMINI_API_KEY is set to "" so no client can be built (Demo / replay mode).
_GEMINI_PLACEHOLDERS = {
    "your_key_here", "your-key-here", "yourkey", "your_api_key", "your-api-key", "api_key",
    "changeme", "change_me", "change-me", "replace_me", "replace-me", "placeholder", "none",
    "null", "xxx", "todo", "test", "demo", "example",
}
# Letters, digits and the URL-safe marks Google keys may use (. _ - ~). No spaces, no quotes.
_GEMINI_PLACEHOLDER_STARTS = ("your", "paste", "enter", "insert", "replace", "change", "put")
_GEMINI_KEY_SHAPE = re.compile(r"^[A-Za-z0-9_.~\-]{20,200}$")


def _usable_gemini_key(raw):
    key = (raw or "").strip()
    if not key or key.lower() in _GEMINI_PLACEHOLDERS or key.lower().startswith(_GEMINI_PLACEHOLDER_STARTS):
        return ""
    return key if _GEMINI_KEY_SHAPE.match(key) else ""


GEMINI_API_KEY = _usable_gemini_key(env.str("GEMINI_API_KEY", default=""))
GEMINI_KEY_PRESENT = bool(GEMINI_API_KEY)
# The model name is a setting (docs/ai-model-choice.md). Fallback: gemini-3.1-flash-lite (untested).
GEMINI_MODEL = env.str("GEMINI_MODEL", default="").strip() or "gemini-3.5-flash-lite"

# AI bounds (AD-4.5), in seconds, and the prompt size backstop (AD-5.6).
AI_CALL_TIMEOUT_S = env.int("AI_CALL_TIMEOUT_S", default=60)
RATE_WAIT_MAX_S = env.int("RATE_WAIT_MAX_S", default=90)
AI_JOB_BUDGET_S = env.int("AI_JOB_BUDGET_S", default=220)


def _retry_waits(raw):
    """Parse the waits before each retry of a busy provider (503 or 429), e.g. "2,5,10" -> (2, 5, 10).

    One number per retry, so the list length is the number of retries (1 to 5). Bad text stops the start.
    """
    try:
        waits = tuple(int(part) for part in str(raw).split(","))
    except ValueError:
        raise ImproperlyConfigured("AI_RETRY_WAITS_S must be whole seconds separated by commas, like 2,5,10.") from None
    if not 1 <= len(waits) <= 5 or any(not 0 <= wait <= 60 for wait in waits):
        raise ImproperlyConfigured("AI_RETRY_WAITS_S needs 1 to 5 numbers, each from 0 to 60 seconds.")
    return waits


# The waits before each retry after a 503 or 429 (3 retries). Always inside the job budget.
AI_RETRY_WAITS_S = _retry_waits(env.str("AI_RETRY_WAITS_S", default="2,5,10"))
MAX_PROMPT_CHARS = env.int("MAX_PROMPT_CHARS", default=200000)
# Free-tier limits read from the builder's AI Studio page on 2026-11-25 (docs/ai-model-choice.md).
AI_REQUESTS_PER_MINUTE = env.int("AI_REQUESTS_PER_MINUTE", default=15)
AI_REQUESTS_PER_DAY = env.int("AI_REQUESTS_PER_DAY", default=500)
