"""Checks for AI output (AD-4.4, AD-5). Pure: no models, no request, no network.

A failure carries a short reason code and at most a part number, never any text from the answer
or from the slides, so it is safe to log and to show (AD-15.2).
"""

from .text_utils import normalize_text
from .types import SourceRef

LANGUAGES = ("en", "nb")
MAX_PARTS = 30
MAX_TERMS_PER_PART = 12
MAX_HEADING = 300
MAX_TEXT = 4000
MAX_TERM = 200
MAX_EXPLANATION = 1000
# Real links, angle brackets and htmx attributes (user decision, 2026-11-25): the plain word "HTTP" is allowed,
# so a lecture about HTTP can work (AD-5.4 narrowed).
FORBIDDEN_FRAGMENTS = ("http://", "https://", "www.", "<", ">", "hx-")


class ValidationFailed(Exception):
    """The answer is not usable. `reason` is a short code; `str()` is the same code."""

    def __init__(self, reason, part=None):
        self.reason = reason
        self.part = part
        super().__init__(reason if part is None else f"{reason} (part {part})")


def _text(value, limit, reason, part):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValidationFailed(reason, part)
    lowered = value.lower()
    if any(fragment in lowered for fragment in FORBIDDEN_FRAGMENTS):
        raise ValidationFailed("forbidden_text", part)
    return value.strip()


def validate_summary(output, page_texts):
    """Return the checked Summary as plain dicts, or raise ValidationFailed.

    `page_texts` is the extracted text of each slide in order, so its length is the page count.
    Result: {"language", "parts": [{"order", "heading", "text", "source_refs", "key_terms": [...]}]}.
    """
    page_count = len(page_texts)
    if not isinstance(output, dict) or set(output) != {"language", "parts"}:
        raise ValidationFailed("structure")
    if output["language"] not in LANGUAGES:
        raise ValidationFailed("language")
    parts = output["parts"]
    if not isinstance(parts, list) or not 1 <= len(parts) <= MAX_PARTS:
        raise ValidationFailed("structure")
    lecture_text = normalize_text(" ".join(page_texts))

    checked = []
    for number, part in enumerate(parts, start=1):
        if not isinstance(part, dict) or set(part) != {"heading", "text", "slides", "key_terms"}:
            raise ValidationFailed("structure", number)
        heading = _text(part["heading"], MAX_HEADING, "heading", number)
        text = _text(part["text"], MAX_TEXT, "text", number)
        try:
            refs = SourceRef.from_numbers(part["slides"], page_count)
        except ValueError:
            raise ValidationFailed("slides", number) from None
        terms = part["key_terms"]
        if not isinstance(terms, list) or len(terms) > MAX_TERMS_PER_PART:
            raise ValidationFailed("structure", number)
        checked_terms = []
        for term in terms:
            if not isinstance(term, dict) or set(term) != {"term", "explanation"}:
                raise ValidationFailed("structure", number)
            name = _text(term["term"], MAX_TERM, "term", number)
            explanation = _text(term["explanation"], MAX_EXPLANATION, "explanation", number)
            if normalize_text(name) not in lecture_text:
                raise ValidationFailed("term_not_in_lecture", number)
            checked_terms.append({"term": name, "explanation": explanation})
        checked.append(
            {"order": number, "heading": heading, "text": text,
             "source_refs": refs.as_list(), "key_terms": checked_terms}
        )
    return {"language": output["language"], "parts": checked}
