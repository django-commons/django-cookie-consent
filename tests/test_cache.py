import json

from django.core.cache import caches
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.locmem import LocMemCache
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.test import TestCase, override_settings

from pytest_django.asserts import assertNumQueries

from cookie_consent.cache import (
    CACHE_KEY,
    all_cookie_groups,
    delete_cache,
    get_cookie,
    get_cookie_group,
)
from cookie_consent.models import Cookie, CookieGroup


class CacheTest(TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(delete_cache)

        self.cookie_group = CookieGroup.objects.create(
            varname="optional",
            name="Optional",
        )
        self.cookie = Cookie.objects.create(
            cookiegroup=self.cookie_group,
            name="foo",
        )

    def test_get_cookie_group(self):
        self.assertEqual(get_cookie_group("optional"), self.cookie_group)

    def test_get_cookie(self):
        cookie_group = get_cookie_group("optional")
        self.assertEqual(get_cookie(cookie_group, "foo", ""), self.cookie)

    def test_caching(self):
        CookieGroup.objects.create(
            varname="foo",
            name="Foo",
        )
        with self.assertNumQueries(2):
            cookie_group = get_cookie_group("optional")
            get_cookie_group("foo")
            get_cookie(cookie_group, "foo", "")

    def test_caching_expire(self):
        with self.assertNumQueries(2):
            cookie_group = get_cookie_group("optional")

        self.cookie_group.name = "Bar"
        self.cookie_group.save()

        with self.assertNumQueries(2):
            cookie_group = get_cookie_group("optional")
        self.assertEqual(cookie_group.name, "Bar")

    @override_settings(
        CACHES={"tests": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}},
        COOKIE_CONSENT_CACHE_BACKEND="tests",
    )
    def test_can_override_cache_settings(self):
        """
        Assert that the cache backend/settings can be swapped out in tests.

        Regression test for #41
        """
        CookieGroup.objects.create(
            varname="foo",
            name="Foo",
        )
        # expect multiple calls to not be cached because of the no-op cache
        with self.assertNumQueries(2 + 2):
            get_cookie_group("optional")
            get_cookie_group("foo")


class JSONBasedCacheBackend(LocMemCache):
    """
    Custom cache backend that uses JSON serialization.

    Taken and adapted from
    https://github.com/lazybird/django-solo/blob/34dd290941acdf736545c2b0258e5b39c18783c1/solo/tests/cache_backend.py
    """

    def get(self, key, default=None, version=None):
        value = super().get(key, default=default, version=version)
        if value == default:
            return value
        return json.loads(value)

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        value = json.dumps(value, cls=DjangoJSONEncoder)
        return super().add(key, value, timeout=timeout, version=version)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        if not isinstance(value, models.QuerySet):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        return super().set(key, value, timeout=timeout, version=version)


def test_cache_is_compatible_with_non_pickle_based_backends(
    settings,
    optional_cookiegroup: CookieGroup,
):
    settings.COOKIE_CONSENT_CACHE_BACKEND = "default"
    settings.CACHES = {"default": {"BACKEND": "tests.test_cache.JSONBasedCacheBackend"}}
    CookieGroup.objects.create(
        varname="optional2",
        name="Optional cookies",
        is_required=False,
        is_deletable=True,
    )

    # main query + prefetch query
    with assertNumQueries(2):
        assert len(all_cookie_groups()) == 2

    # cache hit - no more queries
    with assertNumQueries(0):
        assert len(all_cookie_groups()) == 2


def test_old_cache_format_does_not_crash_cache_mechanism(
    settings,
    optional_cookiegroup: CookieGroup,
):
    settings.COOKIE_CONSENT_CACHE_BACKEND = "default"
    settings.CACHES = {"default": {"BACKEND": "tests.test_cache.JSONBasedCacheBackend"}}
    cache = caches["default"]
    # manually set garbage data that should be ignored
    cache.set(CACHE_KEY, CookieGroup.objects.all(), timeout=60)

    # main query + prefetch query, despite cache data being present, it should be
    # ignored and be refreshed
    with assertNumQueries(2):
        assert len(all_cookie_groups()) == 1


def test_related_objects_are_included_in_cache_data(
    settings,
    optional_cookiegroup: CookieGroup,
):
    Cookie.objects.create(cookiegroup=optional_cookiegroup, name="foo")
    # warm cache
    assert bool(all_cookie_groups())

    with assertNumQueries(0):
        cookie_group = get_cookie_group("optional")
        assert cookie_group is not None
        get_cookie_group("foo")
        get_cookie(cookie_group, "foo", "")
