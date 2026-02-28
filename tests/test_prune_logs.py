from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.utils import timezone

import pytest

from cookie_consent.models import ACTION_ACCEPTED, LogItem


@pytest.fixture
def make_log_item(optional_cookiegroup):
    def _make(days_old: int) -> LogItem:
        item = LogItem.objects.create(
            action=ACTION_ACCEPTED,
            cookiegroup=optional_cookiegroup,
            version="1",
        )
        LogItem.objects.filter(pk=item.pk).update(
            created=timezone.now() - timedelta(days=days_old)
        )
        return item

    return _make


def test_prunes_old_items_with_default_days(make_log_item):
    old = make_log_item(days_old=91)
    recent = make_log_item(days_old=10)

    call_command("prune_logs")

    assert not LogItem.objects.filter(pk=old.pk).exists()
    assert LogItem.objects.filter(pk=recent.pk).exists()


def test_prunes_items_older_than_custom_days(make_log_item):
    old = make_log_item(days_old=31)
    recent = make_log_item(days_old=5)

    call_command("prune_logs", days=30)

    assert not LogItem.objects.filter(pk=old.pk).exists()
    assert LogItem.objects.filter(pk=recent.pk).exists()


def test_no_items_deleted_when_all_recent(make_log_item):
    item = make_log_item(days_old=1)

    call_command("prune_logs")

    assert LogItem.objects.filter(pk=item.pk).exists()


def test_output_reports_deleted_count(make_log_item):
    make_log_item(days_old=91)
    make_log_item(days_old=91)

    out = StringIO()
    call_command("prune_logs", stdout=out)

    assert "2" in out.getvalue()
