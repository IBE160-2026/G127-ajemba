from django.core.management.base import BaseCommand

from lectures.services import reap_stale


class Command(BaseCommand):
    help = "Mark lectures stuck in 'processing' for longer than STALE_MINUTES as failed (AD-3.7)."

    def handle(self, *args, **options):
        self.stdout.write(f"Stuck lectures marked as failed: {reap_stale()}")
