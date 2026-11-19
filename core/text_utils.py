"""Text cleaning in one place (AD-21). Pure: no models, no request, no network."""

import re
import unicodedata

SOFT_HYPHEN = "\u00ad"
_SOFT_HYPHEN_AT_LINE_BREAK = re.compile(SOFT_HYPHEN + r"[ \t]*\r?\n[ \t]*")
_HYPHEN_AT_LINE_BREAK = re.compile(r"(?<=\w)-[ \t]*\r?\n[ \t]*(?=\w)")
_WHITESPACE = re.compile(r"\s+")


def normalize_text(text):
    """NFKC, soft hyphens removed, words split at a line break joined, case-folded, single-spaced.

    NFKC turns ligature glyphs (the "fi" and "fl" characters) into plain letters.
    """
    text = unicodedata.normalize("NFKC", text)
    text = _SOFT_HYPHEN_AT_LINE_BREAK.sub("", text)
    text = text.replace(SOFT_HYPHEN, "")
    text = _HYPHEN_AT_LINE_BREAK.sub("", text)
    text = text.casefold()
    return _WHITESPACE.sub(" ", text).strip()
