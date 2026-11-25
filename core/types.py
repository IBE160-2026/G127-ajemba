"""Shared shapes for the pure modules (AD-2.3, AD-21). Frozen dataclasses; no models, no network.

Story 4.1 adds the other dataclasses (AnswerRecord, QuestionRecord, AttemptResult) to this file.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceRef:
    """The sorted, de-duplicated slide numbers a part rests on: every number, never range ends."""

    slides: tuple

    @classmethod
    def from_numbers(cls, numbers, page_count):
        """Build a SourceRef, or raise ValueError when a number is not a whole slide in 1..page_count."""
        if not isinstance(numbers, (list, tuple)) or not numbers:
            raise ValueError("no slide numbers")
        for number in numbers:
            if isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= page_count:
                raise ValueError("slide number out of range")
        return cls(tuple(sorted(set(numbers))))

    def as_list(self):
        return list(self.slides)
