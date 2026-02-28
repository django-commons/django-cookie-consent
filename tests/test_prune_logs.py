from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from cookie_consent.models import ACTION_ACCEPTED, Cookie, CookieGroup, LogItem


class PruneLogsCommandTest(TestCase):
    def setUp(self):
        self.cookie_group = CookieGroup.objects.create(
            varname="optional",
            name="Optional cookies",
        )
        Cookie.objects.create(cookiegroup=self.cookie_group, name="evil-tracking")

    def _make_log_item(self, days_old: int) -> LogItem:
        item = LogItem.objects.create(
            action=ACTION_ACCEPTED,
            cookiegroup=self.cookie_group,
            version="1",
        )
        LogItem.objects.filter(pk=item.pk).update(
            created=timezone.now() - timedelta(days=days_old)
        )
        return item

    def test_prunes_old_items_with_default_days(self):
        old = self._make_log_item(days_old=91)
        recent = self._make_log_item(days_old=10)

        call_command("prune_logs")

        self.assertFalse(LogItem.objects.filter(pk=old.pk).exists())
        self.assertTrue(LogItem.objects.filter(pk=recent.pk).exists())

    def test_prunes_items_older_than_custom_days(self):
        old = self._make_log_item(days_old=31)
        recent = self._make_log_item(days_old=5)

        call_command("prune_logs", days=30)

        self.assertFalse(LogItem.objects.filter(pk=old.pk).exists())
        self.assertTrue(LogItem.objects.filter(pk=recent.pk).exists())

    def test_no_items_deleted_when_all_recent(self):
        item = self._make_log_item(days_old=1)

        call_command("prune_logs")

        self.assertTrue(LogItem.objects.filter(pk=item.pk).exists())

    def test_output_reports_deleted_count(self):
        self._make_log_item(days_old=91)
        self._make_log_item(days_old=91)

        out = StringIO()
        call_command("prune_logs", stdout=out)

        self.assertIn("2", out.getvalue())
