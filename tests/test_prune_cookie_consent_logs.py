from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.utils import timezone

import pytest

from cookie_consent.models import ACTION_ACCEPTED, LogItem


@pytest.fixture
def make_log_item(optional_cookiegroup):
    def _make(days_old: int = 0, **kwargs) -> LogItem:
        item = LogItem.objects.create(
            action=ACTION_ACCEPTED,
            cookiegroup=optional_cookiegroup,
            version="1",
        )
        created = timezone.now() - timedelta(days=days_old, **kwargs)
        LogItem.objects.filter(pk=item.pk).update(created=created)
        return item

    return _make


def test_prunes_old_items_with_default_days(make_log_item):
    old = make_log_item(days_old=91)
    recent = make_log_item(days_old=10)

    call_command("prune_cookie_consent_logs", stdout=StringIO(), stderr=StringIO())

    assert not LogItem.objects.filter(pk=old.pk).exists()
    assert LogItem.objects.filter(pk=recent.pk).exists()


def test_prunes_items_older_than_custom_days(make_log_item):
    old = make_log_item(days_old=31)
    recent = make_log_item(days_old=5)

    call_command(
        "prune_cookie_consent_logs", days=30, stdout=StringIO(), stderr=StringIO()
    )

    assert not LogItem.objects.filter(pk=old.pk).exists()
    assert LogItem.objects.filter(pk=recent.pk).exists()


def test_no_items_deleted_when_all_recent(make_log_item):
    item = make_log_item(days_old=1)

    call_command("prune_cookie_consent_logs", stdout=StringIO(), stderr=StringIO())

    assert LogItem.objects.filter(pk=item.pk).exists()


def test_output_reports_deleted_count(make_log_item):
    make_log_item(days_old=91)
    make_log_item(days_old=91)

    out = StringIO()
    call_command("prune_cookie_consent_logs", stdout=out)

    assert out.getvalue().strip() == "Deleted 2 log item(s) older than 90 days."


def test_strict_days_cutoff(make_log_item):
    """
    Test that the cutoff is strict and doesn't just look at the date part.
    """
    # Item created exactly 90 days ago + 4 hour (outside the prune window, so deleted)
    old = make_log_item(days_old=90, hours=4)
    # Item created exactly 90 days ago - 1 hour (inside the prune window, so kept)
    recent = make_log_item(days_old=89, hours=23)

    call_command("prune_cookie_consent_logs", stdout=StringIO(), stderr=StringIO())

    assert not LogItem.objects.filter(pk=old.pk).exists()
    assert LogItem.objects.filter(pk=recent.pk).exists()
