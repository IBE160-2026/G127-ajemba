"""Start Recall with one command: python run.py (AD-15).

Checks the Python version, runs migrate, then starts the web app. Ctrl+C stops the web app and
everything it started. Uses only the standard library, so it works the same on Windows.
"""

import argparse
import os
import signal
import subprocess
import sys
import time

SUPPORTED = ((3, 12), (3, 13))
DEFAULT_PORT = 8000
# After Ctrl+C the server gets this long to stop by itself before it is stopped by force.
STOP_GRACE_SECONDS = 3
POLL_SECONDS = 0.2

# Windows job object: JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE and JobObjectExtendedLimitInformation.
_KILL_ON_JOB_CLOSE = 0x2000
_EXTENDED_LIMIT_INFORMATION = 9
_job_handle = None  # kept for the life of the process; Windows closes it when the process ends


def bind_children_to_this_process():
    """Windows: make every process started from here die when this process ends, however it ends.

    Without this, killing run.py (closing the window, a crash, taskkill) leaves the web server
    running in the background, because the server is a child of a child of run.py.
    Returns True if it worked. If it does not, run.py still stops the server on Ctrl+C.
    """
    global _job_handle
    if os.name != "nt":
        return False

    import ctypes
    from ctypes import wintypes

    class BasicLimits(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimits),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]

    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return False
    limits = ExtendedLimits()
    limits.BasicLimitInformation.LimitFlags = _KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(
        job, _EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits), ctypes.sizeof(limits)
    ):
        return False
    # Put this process in the job first, so every child it starts afterwards is in it too.
    if not kernel32.AssignProcessToJobObject(job, kernel32.GetCurrentProcess()):
        return False
    _job_handle = job
    return True


def stop_server(server):
    """Give the server a moment to stop by itself, then stop it and its children by force."""
    try:
        server.wait(timeout=STOP_GRACE_SECONDS)
        return
    except subprocess.TimeoutExpired:
        pass
    if os.name == "nt":
        # /T also ends the processes the server started.
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(server.pid)], capture_output=True)
    else:
        server.terminate()
    try:
        server.wait(timeout=STOP_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        server.kill()


def _raise_keyboard_interrupt(signum, frame):
    raise KeyboardInterrupt


def serve(port=DEFAULT_PORT, migrate=True):
    """Run migrate (unless told not to), then the web app, until Ctrl+C or the server ends."""
    bind_children_to_this_process()
    if hasattr(signal, "SIGBREAK"):  # Ctrl+Break on Windows behaves like Ctrl+C
        signal.signal(signal.SIGBREAK, _raise_keyboard_interrupt)

    manage = [sys.executable, "manage.py"]
    server = None
    try:
        if migrate:
            print("Preparing the database (migrate)...")
            result = subprocess.run(manage + ["migrate"])
            if result.returncode != 0:
                return result.returncode

        print(f"Starting the web app at http://localhost:{port}/ (press Ctrl+C to stop)")
        server = subprocess.Popen(manage + ["runserver", "--noreload", str(port)])
        # Wait in short rounds. A plain wait() cannot be interrupted by Ctrl+C on Windows.
        while server.poll() is None:
            time.sleep(POLL_SECONDS)
        return server.returncode
    except KeyboardInterrupt:
        print("\nStopping the web app...")
        if server is not None:
            stop_server(server)
        return 0


def main():
    if sys.version_info[:2] not in SUPPORTED:
        found = f"{sys.version_info[0]}.{sys.version_info[1]}"
        print(
            f"Recall needs Python 3.12 or 3.13. You are running Python {found}.\n"
            "Install a supported version and see the README, section 'Install and start'."
        )
        return 1

    try:
        import django  # noqa: F401
    except ImportError:
        print(
            "Django is not installed in this Python.\n"
            "Activate the virtual environment and run: pip install -r requirements.txt\n"
            "See the README, section 'Install and start'."
        )
        return 1

    parser = argparse.ArgumentParser(description="Start Recall.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="port for the web app (default 8000)")
    args = parser.parse_args()
    return serve(args.port)


if __name__ == "__main__":
    sys.exit(main())
