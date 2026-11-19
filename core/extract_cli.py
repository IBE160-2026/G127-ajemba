"""Run in a separate process by lectures.services so a hostile PDF can be stopped (AD-20).

Usage: python -I core/extract_cli.py <pdf path>. Prints the pages as a JSON list on stdout.
Any failure (encrypted, corrupt, ...) exits non-zero.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_text import extract_pages  # noqa: E402

if __name__ == "__main__":
    sys.stdout.write(json.dumps(extract_pages(sys.argv[1])))
