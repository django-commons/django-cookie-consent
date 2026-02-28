from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from cookie_consent.models import LogItem


class Command(BaseCommand):
    help = "Prune old LogItem records older than a given number of days."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Delete log items older than this many days (default: 90).",
        )

    def handle(self, *args, **options):
        days = options["days"]
        cutoff = timezone.now() - timedelta(days=days)
        deleted, _ = LogItem.objects.filter(created__lt=cutoff).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted} log item(s) older than {days} days.")
        )
