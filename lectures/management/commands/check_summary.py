from django.core.management.base import BaseCommand, CommandError

from lectures.models import Lecture
from lectures.services import check_source_refs


class Command(BaseCommand):
    help = "Check that every Source Reference slide of a stored Summary exists in the PDF (SM-2). No AI call."

    def add_arguments(self, parser):
        parser.add_argument("lecture_id", type=int)

    def handle(self, *args, **options):
        lecture_id = options["lecture_id"]
        if not Lecture.objects.filter(pk=lecture_id).exists():
            raise CommandError("No such lecture.")
        problems = check_source_refs(lecture_id)
        if problems:
            raise CommandError("Problems found: " + "; ".join(problems))
        self.stdout.write("OK: every Source Reference slide exists in the PDF.")
