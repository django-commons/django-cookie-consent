from collections.abc import Mapping

from django.core.cache import caches

from .conf import settings
from .models import Cookie, CookieGroup

CACHE_KEY = "cookie_consent_cache"
CACHE_TIMEOUT = 60 * 60  # 60 minutes


def _get_cache():
    """
    Lazily wrap around django.core.cache.

    This prevents the cache object to be resolved at import-time, which breaks the
    `django.test.override_settings` functionality for projects adding tests for this
    package, see https://github.com/bmihelac/django-cookie-consent/issues/41.
    """
    return caches[settings.COOKIE_CONSENT_CACHE_BACKEND]


def delete_cache() -> None:
    cache = _get_cache()
    cache.delete(CACHE_KEY)


def _get_cookie_groups_from_db() -> Mapping[str, CookieGroup]:
    qs = CookieGroup.objects.filter(is_required=False).prefetch_related("cookie_set")
    return qs.in_bulk(field_name="varname")


def all_cookie_groups() -> Mapping[str, CookieGroup]:
    """
    Get all cookie groups that are optional.

    Reads from the cache where possible, sets the value in the cache if there's a
    cache miss.
    """
    cache = _get_cache()
    result = cache.get_or_set(
        CACHE_KEY, _get_cookie_groups_from_db, timeout=CACHE_TIMEOUT
    )
    assert result is not None
    return result


def get_cookie_group(varname: str) -> CookieGroup | None:
    return all_cookie_groups().get(varname)


def get_cookie(cookie_group: CookieGroup, name: str, domain: str) -> Cookie | None:
    # loop over cookie set relation instead of doing a lookup query, as this should
    # come from the cache and avoid hitting the database
    for cookie in cookie_group.cookie_set.all():
        if cookie.name == name and cookie.domain == domain:
            return cookie
    return None
