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


def format_slides(slides):
    """Write slide numbers for a source chip (AD-21): "Slides 12 to 15", "Slides 3, 7 and 12".

    Only a run of three or more consecutive numbers becomes "a to b". Pure; takes any list of whole
    numbers (a SourceRef's `slides` too) and sorts and de-duplicates them first.
    """
    numbers = sorted(set(slides))
    if not numbers:
        return ""
    groups = []  # each item is a list of consecutive numbers
    for number in numbers:
        if groups and number == groups[-1][-1] + 1:
            groups[-1].append(number)
        else:
            groups.append([number])
    pieces = []
    for run in groups:
        if len(run) >= 3:
            pieces.append(f"{run[0]} to {run[-1]}")
        else:
            pieces.extend(str(n) for n in run)
    if len(pieces) == 1:
        text = pieces[0]
    else:
        text = ", ".join(pieces[:-1]) + " and " + pieces[-1]
    return ("Slide " if len(numbers) == 1 else "Slides ") + text
