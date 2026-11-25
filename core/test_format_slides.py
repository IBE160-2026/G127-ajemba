from django.test import SimpleTestCase

from .text_utils import format_slides


class FormatSlidesTests(SimpleTestCase):
    def test_format_slides_runs_and_lists(self):
        cases = {
            (12, 13, 14, 15): "Slides 12 to 15",
            (3, 7, 12): "Slides 3, 7 and 12",
            (4, 5): "Slides 4 and 5",
            (9,): "Slide 9",
            (1, 2, 3, 7): "Slides 1 to 3 and 7",
            (1, 2, 5): "Slides 1, 2 and 5",
            (7, 1, 2, 3, 3): "Slides 1 to 3 and 7",
            (2, 3, 4, 8, 9, 10): "Slides 2 to 4 and 8 to 10",
            (): "",
        }
        for numbers, expected in cases.items():
            self.assertEqual(format_slides(list(numbers)), expected, numbers)
