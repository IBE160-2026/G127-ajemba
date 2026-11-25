# django-q2 on Windows (story 3.2, AD-3.3)

**Question:** does the django-q2 cluster run on Windows, so the thread-based fallback is not needed?

**Answer: yes.** The thread-based fallback was not built.

- **Date:** 2026-11-25. **System:** Windows 11 (10.0.26200), Python 3.13.2, Django 5.2.18, django-q2 1.11.1, django-picklefield 3.4.0 (both MIT).
- **Settings tested:** one worker, `timeout` 240, `retry` 300, `max_attempts` 1, `ack_failures` on, `save_limit` -1, ORM broker on SQLite (names checked in the installed `django_q/conf.py`).

## What was run

1. `lectures.test_processing.RealWorkerTests.test_fr5_job_finishes_after_page_closed`: a throwaway database, a lecture in `processing`, the same job queued twice, **no web server running**, then a real `manage.py qcluster`. Result: the lecture ended as `failed` exactly once (the stub job), the queue table was empty, and no successful task was stored.
2. `config.tests.RunPyStopsServerTests`: `run.py` starts the web app and the worker. Ctrl+Break stops both; killing `run.py` stops both; killing the worker makes `run.py` stop the web app.

## Notes

- django-q2 prints a warning if `retry` is not larger than `timeout`; the settings keep it larger.
- The queue holds only the job name and an integer id.
- Not tested: macOS and Linux, and a real Ctrl+C typed in a terminal (Ctrl+Break is tested, and uses the same clean-up). Both are for the manual check.
