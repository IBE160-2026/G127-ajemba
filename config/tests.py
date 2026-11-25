import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.db.utils import ConnectionHandler
from django.test import SimpleTestCase, TestCase

BASE_DIR = Path(settings.BASE_DIR)


def _load_settings_in_subprocess(**env_overrides):
    """Import config.settings in a fresh Python so the start-up checks run again."""
    env = os.environ.copy()
    for name in ("RECALL_ENV", "SECRET_KEY"):
        env.pop(name, None)
    # Point at a missing file so a developer's own .env cannot change the result.
    env["RECALL_ENV_FILE"] = str(BASE_DIR / "no-such-env-file")
    env["DJANGO_SETTINGS_MODULE"] = "config.settings"
    env.update(env_overrides)
    code = "from django.conf import settings; print(bool(settings.SECRET_KEY))"
    return subprocess.run(
        [sys.executable, "-c", code], cwd=BASE_DIR, env=env, capture_output=True, text=True
    )


class HomePageTests(TestCase):
    def test_home_page_returns_200(self):
        """Story 1.1 criterion 3: the home page opens."""
        self.assertEqual(self.client.get("/").status_code, 200)


class SettingsTests(SimpleTestCase):
    def test_settings_refuse_missing_secret_when_not_local(self):
        """AD-12, story 1.1 criterion 5."""
        result = _load_settings_in_subprocess(RECALL_ENV="production")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY is missing", result.stderr)

    def test_settings_start_without_env_file_when_local(self):
        """AD-12.4: the app starts with no .env."""
        result = _load_settings_in_subprocess()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_settings_accept_secret_when_not_local(self):
        result = _load_settings_in_subprocess(RECALL_ENV="production", SECRET_KEY="x" * 50)
        self.assertEqual(result.returncode, 0, result.stderr)


class SqliteTests(SimpleTestCase):
    databases = {"default"}

    def test_sqlite_pragmas_set(self):
        """AD-24, story 1.1 criterion 7."""
        options = settings.DATABASES["default"]["OPTIONS"]
        self.assertEqual(options["timeout"], 20)
        self.assertEqual(options["transaction_mode"], "IMMEDIATE")

        # The test database lives in memory, where WAL does not apply, so check
        # synchronous and foreign_keys here and journal_mode on a real file below.
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA synchronous")
            self.assertEqual(cursor.fetchone()[0], 1)  # 1 = NORMAL
            cursor.execute("PRAGMA foreign_keys")
            self.assertEqual(cursor.fetchone()[0], 1)

        folder = tempfile.mkdtemp()
        try:
            config = dict(settings.DATABASES["default"], NAME=str(Path(folder) / "wal.sqlite3"))
            handler = ConnectionHandler({"default": config})
            file_connection = handler["default"]
            try:
                with file_connection.cursor() as cursor:
                    cursor.execute("PRAGMA journal_mode")
                    self.assertEqual(cursor.fetchone()[0].lower(), "wal")
            finally:
                file_connection.close()
        finally:
            shutil.rmtree(folder, ignore_errors=True)


class GitHygieneTests(SimpleTestCase):
    def _git(self, *args):
        return subprocess.run(["git", *args], cwd=BASE_DIR, capture_output=True, text=True)

    def test_env_file_not_tracked_by_git(self):
        """AD-12.6, story 1.1 criterion 6."""
        if shutil.which("git") is None:
            self.skipTest("git is not installed, so tracking cannot be checked")
        if self._git("rev-parse", "--is-inside-work-tree").returncode != 0:
            self.skipTest("not a git repository, so tracking cannot be checked")

        self.assertEqual(self._git("ls-files", ".env").stdout.strip(), "")
        for path in (".env", "db.sqlite3", "logs/web.log"):
            ignored = self._git("check-ignore", "-q", path)
            self.assertEqual(ignored.returncode, 0, f"{path} is not ignored by git")

    def test_gitattributes_and_requirements(self):
        """Story 1.1 criterion 6: LF endings and exact versions."""
        attributes = (BASE_DIR / ".gitattributes").read_text(encoding="utf-8")
        for pattern in ("*.md", "*.json", "*.txt"):
            self.assertIn(f"{pattern} text eol=lf", attributes)

        lines = (BASE_DIR / "requirements.txt").read_text(encoding="utf-8").splitlines()
        for line in (l.strip() for l in lines):
            if line and not line.startswith("#"):
                self.assertRegex(line, r"^[A-Za-z0-9_.\-]+==\d+(\.\d+)*$", line)


class ReadmeTests(SimpleTestCase):
    def test_readme_has_required_sections(self):
        """Story 1.1 criterion 8. Every later story adds its heading to the list."""
        headings_file = BASE_DIR / "docs" / "required_readme_headings.txt"
        headings = [h.strip() for h in headings_file.read_text(encoding="utf-8").splitlines() if h.strip()]
        self.assertEqual(headings[0], "Install and start")

        readme = (BASE_DIR / "README.md").read_text(encoding="utf-8")
        found = {line.lstrip("#").strip() for line in readme.splitlines() if line.startswith("#")}
        for heading in headings:
            self.assertIn(heading, found, f"README.md is missing the section '{heading}'")


# Starts run.serve() (without migrate, so the real db.sqlite3 is not touched) in a child Python.
# If a file named by the second argument appears, the child dies at once, with no clean-up,
# like a closed terminal window or a killed process.
_SERVE_WRAPPER = """
import os, sys, threading, time
import run
port, flag, pidfile = int(sys.argv[1]), sys.argv[2], sys.argv[3]
def started(children):
    with open(pidfile, "w") as f:
        f.write(" ".join(str(c.pid) for c in children))
def watch():
    while not os.path.exists(flag):
        time.sleep(0.1)
    os._exit(1)
threading.Thread(target=watch, daemon=True).start()
sys.exit(run.serve(port, migrate=False, on_start=started))
"""


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _port_open(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _wait_for(condition, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.2)
    return condition()


class RunPyCleanUpTests(SimpleTestCase):
    """AD-15.1: if starting the worker fails, the web app that already started is stopped."""

    def test_server_is_stopped_when_the_worker_cannot_start(self):
        import run
        from unittest import mock

        server = mock.MagicMock()
        server.poll.return_value = None  # still running
        popen = mock.MagicMock(side_effect=[server, OSError("cannot start the worker")])
        with mock.patch.object(run.subprocess, "Popen", popen),                 mock.patch.object(run, "bind_children_to_this_process"),                 mock.patch.object(run, "stop_process") as stop:
            with self.assertRaises(OSError):
                run.serve(port=1, migrate=False)
        stop.assert_called_once_with(server)


def _pid_alive(pid):
    out = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], capture_output=True, text=True
    ).stdout
    # CSV rows look like "python.exe","1234","Console",... ; a missing process gives an INFO line.
    return any(line.split('","')[1:2] == [str(pid)] for line in out.splitlines())


@unittest.skipUnless(os.name == "nt", "run.py stopping its children is a Windows concern")
class RunPyStopsServerTests(SimpleTestCase):
    """AD-15.1: run.py stops the web app, the worker and everything they started."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The worker reads a throwaway database, so the real db.sqlite3 is not touched.
        cls.folder = tempfile.mkdtemp()
        cls.db_file = str(Path(cls.folder) / "test.sqlite3")
        env = {**os.environ, "DATABASE_FILE": cls.db_file, "RECALL_ENV_FILE": str(BASE_DIR / "no-such-env-file")}
        for name in ("RECALL_ENV", "SECRET_KEY"):
            env.pop(name, None)
        cls.env = env
        subprocess.run([sys.executable, "manage.py", "migrate", "-v", "0"], cwd=BASE_DIR, env=env, check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.folder, ignore_errors=True)
        super().tearDownClass()

    def _start(self, flag, **popen_options):
        port = _free_port()
        pidfile = Path(self.folder) / f"pids-{port}.txt"
        proc = subprocess.Popen(
            [sys.executable, "-c", _SERVE_WRAPPER, str(port), str(flag), str(pidfile)],
            cwd=BASE_DIR, env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **popen_options,
        )
        self.addCleanup(
            lambda: subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        )
        started = _wait_for(lambda: _port_open(port) and pidfile.exists(), 30)
        self.assertTrue(started, "the web app did not start")
        with urllib.request.urlopen(f"http://localhost:{port}/", timeout=5) as response:
            self.assertEqual(response.status, 200)
        server_pid, worker_pid = (int(p) for p in pidfile.read_text().split())
        self.assertTrue(_pid_alive(worker_pid), "the worker did not start")
        return proc, port, server_pid, worker_pid

    def test_server_and_worker_die_when_run_py_is_killed(self):
        """Story 1.1 bug: killing run.py must not leave the server or the worker running."""
        flag = Path(self.folder) / "die"
        proc, port, server_pid, worker_pid = self._start(flag)
        flag.write_text("now")
        self.assertTrue(_wait_for(lambda: not _port_open(port), 15), "the server kept running after run.py was killed")
        self.assertTrue(_wait_for(lambda: not _pid_alive(worker_pid), 15), "the worker kept running after run.py was killed")

    def test_ctrl_break_stops_run_py_server_and_worker(self):
        """AC 8: Ctrl+Break goes through the same clean-up as Ctrl+C and stops both."""
        proc, port, server_pid, worker_pid = self._start(
            Path(self.folder) / "unused", creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        os.kill(proc.pid, signal.CTRL_BREAK_EVENT)
        self.assertTrue(_wait_for(lambda: proc.poll() is not None, 20), "run.py did not exit")
        self.assertTrue(_wait_for(lambda: not _port_open(port), 5), "the server kept running")
        self.assertTrue(_wait_for(lambda: not _pid_alive(worker_pid), 5), "the worker kept running")

    def test_run_py_stops_the_server_when_the_worker_ends(self):
        """If one of the two ends, the other is stopped too."""
        proc, port, server_pid, worker_pid = self._start(Path(self.folder) / "unused")
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(worker_pid)], capture_output=True)
        self.assertTrue(_wait_for(lambda: proc.poll() is not None, 20), "run.py kept running without its worker")
        self.assertTrue(_wait_for(lambda: not _port_open(port), 10), "the server kept running without its worker")


class BasePageTests(TestCase):
    """Story 1.2 AC 8: the base page is safe for htmx (AD-19)."""

    def test_csp_header_and_csrf_header_on_base_page(self):
        response = self.client.get("/")
        self.assertEqual(
            response["Content-Security-Policy"],
            "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'",
        )
        html = response.content.decode()
        self.assertRegex(html, r"<body hx-headers='\{\"X-CSRFToken\": \"[^\"]+\"\}'>")
        # htmx settings, set in a meta tag because inline scripts are forbidden by the CSP.
        for setting in ('"allowEval": false', '"selfRequestsOnly": true', '"historyCacheSize": 0'):
            self.assertIn(setting, html)
        self.assertNotIn("<script>", html)
        self.assertNotIn("http://", html.replace("http://testserver", ""))
        self.assertNotIn("https://", html)

    def test_htmx_is_the_recorded_file_kept_in_the_repository(self):
        import base64
        import hashlib

        vendor = BASE_DIR / "static" / "vendor"
        data = (vendor / "htmx.min.js").read_bytes()
        digest = "sha384-" + base64.b64encode(hashlib.sha384(data).digest()).decode()
        note = (vendor / "htmx.SOURCE.txt").read_text(encoding="utf-8")
        self.assertIn(digest, note)
        self.assertIn("2.0.10", note)
        self.assertIn(b'version:"2.0.10"', data)

    def test_logout_script_clears_recall_and_htmx_history_keys(self):
        """AD-19.3. The real clearing is a manual browser check; this guards the key prefixes."""
        script = (BASE_DIR / "static" / "js" / "logout.js").read_text(encoding="utf-8")
        self.assertIn('"recall:"', script)
        self.assertIn('"htmx-history-cache"', script)
        self.assertIn("data-recall-logout", script)
