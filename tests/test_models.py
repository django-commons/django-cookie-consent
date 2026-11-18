import string
from copy import deepcopy

from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

import pytest
from hypothesis import given, strategies as st

from cookie_consent.cache import _CACHE_VERSION, CACHE_KEY, delete_cache
from cookie_consent.models import Cookie, CookieGroup, validate_cookie_name

patch_caches = override_settings(
    COOKIE_CONSENT_CACHE_BACKEND="tests",
    CACHES={
        **deepcopy(settings.CACHES),
        "tests": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    },
)


class CacheMixin:
    def populateCache(self):
        cache = caches["tests"]
        cache.set(CACHE_KEY, {}, timeout=3600, version=_CACHE_VERSION)

    def assertCacheNotPopulated(self):
        cache = caches["tests"]
        has_key = cache.has_key(CACHE_KEY, version=_CACHE_VERSION)
        self.assertFalse(has_key)


@patch_caches
class CookieGroupTest(CacheMixin, TestCase):
    def setUp(self):
        self.addCleanup(delete_cache)

        self.cookie_group = CookieGroup.objects.create(
            varname="optional",
            name="Optional",
        )
        self.cookie = Cookie.objects.create(
            cookiegroup=self.cookie_group,
            name="foo",
        )

    def test_get_version(self):
        self.assertEqual(
            self.cookie_group.get_version(), self.cookie.created.isoformat()
        )

    def test_bulk_delete(self):
        self.populateCache()

        deleted_objs_count, _ = CookieGroup.objects.filter(
            id=self.cookie_group.id
        ).delete()

        # Deleting a CookieGroup also deletes the associated Cookies, that's why we
        # expect a count of 2.
        self.assertEqual(deleted_objs_count, 2)
        self.assertCacheNotPopulated()

    def test_bulk_update(self):
        self.populateCache()

        updated_objs_count = CookieGroup.objects.filter(id=self.cookie_group.id).update(
            name="Optional2"
        )

        self.assertEqual(updated_objs_count, 1)
        self.assertCacheNotPopulated()


@patch_caches
class CookieTest(CacheMixin, TestCase):
    def setUp(self):
        self.addCleanup(delete_cache)

        self.cookie_group = CookieGroup.objects.create(
            varname="optional",
            name="Optional",
        )
        self.cookie = Cookie.objects.create(
            cookiegroup=self.cookie_group,
            name="foo",
            domain=".example.com",
        )

    def test_varname(self):
        self.assertEqual(self.cookie.varname, "optional=foo:.example.com")

    def test_bulk_delete(self):
        self.populateCache()

        deleted_objs_count, _ = Cookie.objects.filter(id=self.cookie.id).delete()

        self.assertEqual(deleted_objs_count, 1)
        self.assertCacheNotPopulated()

    def test_bulk_update(self):
        self.populateCache()

        updated_objs_count = Cookie.objects.filter(id=self.cookie.id).update(
            name="foo2"
        )

        self.assertEqual(updated_objs_count, 1)
        self.assertCacheNotPopulated()


@given(
    name=st.text(
        alphabet=string.ascii_letters + string.digits + "-_",
        min_size=1,
    )
)
def test_valid_cookie_name_does_not_raise(name):
    try:
        validate_cookie_name(name)
    except ValidationError:
        pytest.fail(reason=f"Expected {name} to be valid")


@pytest.mark.parametrize(
    "name",
    (
        "space inside",
        "a!b",
        "$",
    ),
)
def test_invalid_cookie_name_raises(name: str):
    with pytest.raises(ValidationError):
        validate_cookie_name(name)
