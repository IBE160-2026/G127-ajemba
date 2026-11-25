"""Background jobs behind one door (AD-3). The only module that imports django-q2.

A job gets an integer id and returns nothing. No page text, no AI output and no essay text is
ever an argument or a result, so no content is stored in the queue tables.
"""

import logging

from django.db import transaction
from django_q.tasks import async_task

logger = logging.getLogger("recall.jobs")

SUMMARY = "summary"


class JobFailed(Exception):
    """What a failed job raises. Its text is the class name of the real error and nothing else."""


def summary_job(lecture_id):
    """The Summary job: all work is in the service, which claims the lecture first (story 3.3)."""
    from lectures.services import run_summary

    run_summary(lecture_id)


JOBS = {SUMMARY: summary_job}


def run_job(name, object_id):
    """What the worker calls. Checks the arguments again, so a bad queue row does nothing."""
    if name not in JOBS or isinstance(object_id, bool) or not isinstance(object_id, int):
        logger.error("job=%s refused: unknown name or id is not an integer", name)
        return
    try:
        JOBS[name](object_id)
    except Exception as error:
        # django-q2 stores a failed task with the exception text and the traceback, and failed
        # tasks are never pruned. Keep only the class name, so no lecture text can end up there
        # (AD-3.1, AD-15.2). The original error is not chained.
        logger.error("job=%s id=%s failed: %s", name, object_id, type(error).__name__)
        raise JobFailed(type(error).__name__) from None


def enqueue(name, object_id):
    """Queue a job after the surrounding transaction commits, so the row exists first (AD-3.4)."""
    if name not in JOBS:
        raise ValueError(f"Unknown job {name!r}")
    if isinstance(object_id, bool) or not isinstance(object_id, int):
        raise TypeError("A job gets an integer id and nothing else.")
    transaction.on_commit(lambda: _submit(name, object_id))


def _submit(name, object_id):
    async_task("core.jobs.run_job", name, object_id)


def queued_arguments():
    """The arguments of every job waiting in the queue, for tests. Reads the queue, changes nothing."""
    from django_q.models import OrmQ

    return [(q.func(), q.args()) for q in OrmQ.objects.all()]
