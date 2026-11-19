"""The import-boundary test (AD-2.4 and AD-2.7).

It reads the imports of every module without running it, so it works before the guarded
modules exist. Nothing else may import these libraries; the pure modules import no models,
no request and no network.
"""

import ast
import tempfile
import textwrap
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

BASE_DIR = Path(settings.BASE_DIR)

# library prefixes -> the one file allowed to import them
SINGLE_OWNER_RULES = [
    (("google.genai", "google.generativeai"), "core/ai_client.py"),
    (("pypdf",), "core/pdf_text.py"),
    (("django_q",), "core/jobs.py"),
    # pdfplumber is only for the one-off comparison in evaluation/; no app file may import it.
    (("pdfplumber",), None),
]

# Folders that are not app code: evaluation scripts may import pdfplumber and pypdf.
EXEMPT_FOLDERS = {"evaluation"}

# Pure modules in core/ (AD-2.2).
PURE_MODULES = {"scoring", "matching", "review_list", "validation", "text_utils", "types"}
PURE_FORBIDDEN_PREFIXES = (
    "django.db", "django.http", "django.shortcuts", "django.contrib",
    "requests", "httpx", "urllib", "http", "socket", "ssl",
    "google", "pdfplumber", "pypdf", "django_q",
)
# Anything from this project is forbidden in a pure module, except the other pure modules.
PROJECT_PACKAGES_FORBIDDEN = ("accounts", "config", "lectures")


def _matches(name, prefix):
    return name == prefix or name.startswith(prefix + ".")


def imported_names(path):
    """All dotted names a file imports. 'from google import genai' gives 'google.genai' too."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = ("." * node.level) + (node.module or "")
            names.append(module)
            joiner = "" if module.endswith(".") or not module else "."
            names += [f"{module}{joiner}{alias.name}" for alias in node.names]
    return names


def project_python_files(root):
    """Python files in the project's own packages and root scripts, not the virtual environment."""
    files = [p for p in root.glob("*.py")]
    for folder in root.iterdir():
        if folder.is_dir() and (folder / "__init__.py").exists() and not folder.name.startswith("."):
            files += [p for p in folder.rglob("*.py") if "__pycache__" not in p.parts]
    return sorted(files)


def find_import_violations(root):
    """Return a list of plain-text problems; empty means every rule holds."""
    root = Path(root)
    problems = []
    for path in project_python_files(root):
        relative = path.relative_to(root).as_posix()
        if relative.split("/")[0] in EXEMPT_FOLDERS:
            continue
        names = imported_names(path)

        for prefixes, owner in SINGLE_OWNER_RULES:
            if relative == owner:
                continue
            for name in names:
                if any(_matches(name, prefix) for prefix in prefixes):
                    who = f"only {owner} may" if owner else "no app code may"
                    problems.append(f"{relative} imports {name}; {who}")

        is_pure = path.parent.name == "core" and path.stem in PURE_MODULES
        if is_pure and path.parent.parent == root:
            for name in names:
                if name.lstrip(".") == "models" or name.endswith(".models"):
                    problems.append(f"{relative} (pure module) imports models: {name}")
                elif any(_matches(name, p) for p in PURE_FORBIDDEN_PREFIXES + PROJECT_PACKAGES_FORBIDDEN):
                    problems.append(f"{relative} (pure module) imports {name}")
    return sorted(set(problems))


class ImportBoundaryTests(SimpleTestCase):
    def test_ad2_import_boundaries(self):
        """AD-2.4 and AD-2.7: only the named file imports each library; pure modules stay pure."""
        self.assertEqual(find_import_violations(BASE_DIR), [])

    def test_ad2_import_boundaries_detects_violation(self):
        """The check must fail on a deliberately broken example module."""
        with tempfile.TemporaryDirectory() as folder:
            core = Path(folder) / "core"
            core.mkdir()
            (core / "__init__.py").write_text("", encoding="utf-8")
            # Broken: three guarded libraries imported outside their one file.
            (core / "bad_example.py").write_text(
                textwrap.dedent(
                    """
                    import pdfplumber
                    from google import genai
                    from django_q.tasks import async_task
                    import pypdf
                    """
                ),
                encoding="utf-8",
            )
            # Broken: a pure module that touches the database and the project's models.
            (core / "scoring.py").write_text(
                "from django.db import models\nfrom lectures.models import Lecture\n",
                encoding="utf-8",
            )
            # Fine: the evaluation folder is not app code and may import pypdf and pdfplumber.
            evaluation = Path(folder) / "evaluation"
            evaluation.mkdir()
            (evaluation / "__init__.py").write_text("", encoding="utf-8")
            (evaluation / "compare.py").write_text(
                "import pypdf\nimport pdfplumber\n", encoding="utf-8"
            )
            # Fine: each guarded file may import its own library.
            (core / "ai_client.py").write_text("from google import genai\n", encoding="utf-8")
            (core / "pdf_text.py").write_text("import pypdf\n", encoding="utf-8")
            (core / "jobs.py").write_text("import django_q\n", encoding="utf-8")

            problems = find_import_violations(folder)

        text = "\n".join(problems)
        self.assertIn("core/bad_example.py imports pdfplumber; no app code may", text)
        self.assertIn("core/bad_example.py imports google.genai", text)
        self.assertIn("core/bad_example.py imports django_q.tasks", text)
        self.assertIn("core/bad_example.py imports pypdf; only core/pdf_text.py may", text)
        self.assertNotIn("evaluation/", text)
        self.assertIn("core/scoring.py (pure module) imports django.db", text)
        self.assertIn("core/scoring.py (pure module) imports lectures.models", text)
        # The three guarded files import their own library, so no problem is reported about them.
        for allowed in ("ai_client.py", "pdf_text.py", "jobs.py"):
            self.assertFalse(
                [line for line in problems if line.startswith(f"core/{allowed}")], allowed
            )

    def test_ad2_pdf_library_rules_work_both_ways(self):
        """pypdf only in pdf_text.py, pdfplumber nowhere in the app, evaluation/ exempt."""
        with tempfile.TemporaryDirectory() as folder:
            core = Path(folder) / "core"
            core.mkdir()
            (core / "__init__.py").write_text("", encoding="utf-8")
            (core / "pdf_text.py").write_text("import pdfplumber\n", encoding="utf-8")
            (core / "views_like.py").write_text("from pypdf import PdfReader\n", encoding="utf-8")
            problems = "\n".join(find_import_violations(folder))
        self.assertIn("core/pdf_text.py imports pdfplumber; no app code may", problems)
        self.assertIn("core/views_like.py imports pypdf; only core/pdf_text.py may", problems)

        with tempfile.TemporaryDirectory() as folder:
            core = Path(folder) / "core"
            core.mkdir()
            (core / "__init__.py").write_text("", encoding="utf-8")
            (core / "pdf_text.py").write_text("import pypdf\n", encoding="utf-8")
            evaluation = Path(folder) / "evaluation"
            evaluation.mkdir()
            (evaluation / "__init__.py").write_text("", encoding="utf-8")
            (evaluation / "compare.py").write_text(
                "import pypdf\nimport pdfplumber\n", encoding="utf-8"
            )
            self.assertEqual(find_import_violations(folder), [])
