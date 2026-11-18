from __future__ import annotations

import itertools
from collections.abc import Collection, Mapping
from typing import TypedDict

from django.core import serializers
from django.core.cache import caches
from django.db import models, router

from .conf import settings
from .models import Cookie, CookieGroup

CACHE_KEY = "cookie_consent_cache"
CACHE_TIMEOUT = 60 * 60  # 60 minutes

_CACHE_VERSION = 2
"""
Version of the internal cache data format.

Increment this when modifying the cache data (de)serialization logic.
"""


class PythonSerializerData(TypedDict):
    model: str
    pk: int  # concerns only internal cookie consent models, which use int PKs
    fields: Mapping[str, object]


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
    cache.delete(CACHE_KEY, version=_CACHE_VERSION)


def _get_cookie_groups_from_db() -> Collection[PythonSerializerData]:
    qs = CookieGroup.objects.filter(is_required=False).prefetch_related(
        models.Prefetch("cookie_set", to_attr="cookies")
    )
    data = serializers.serialize(
        "python",
        itertools.chain(qs, (cookie for group in qs for cookie in group.cookies)),
    )
    return data


def all_cookie_groups() -> Mapping[str, CookieGroup]:
    """
    Get all cookie groups that are optional.

    Reads from the cache where possible, sets the value in the cache if there's a
    cache miss.
    """
    cache = _get_cache()
    result: Collection[PythonSerializerData] | None = cache.get_or_set(
        CACHE_KEY,
        _get_cookie_groups_from_db,
        timeout=CACHE_TIMEOUT,
        version=_CACHE_VERSION,
    )
    assert result is not None

    deserializer = serializers.deserialize("python", result)
    groups: dict[int, CookieGroup] = {}

    for deserialized_object in deserializer:
        instance = deserialized_object.object
        model_cls = type(instance)
        instance._state.adding = False
        instance._state.db = router.db_for_read(model_cls, instance=instance)

        if isinstance(instance, CookieGroup):
            # mimick m2m prefetch
            instance.cookies = []  # pyright: ignore[reportAttributeAccessIssue]
            groups[instance.pk] = instance
        elif isinstance(instance, Cookie):
            group = groups[instance.cookiegroup_id]  # pyright: ignore[reportAttributeAccessIssue]
            group.cookies.append(instance)  # pyright: ignore[reportAttributeAccessIssue]
            instance.group = group  # pyright: ignore[reportAttributeAccessIssue]
        else:  # pragma: no cover
            raise NotImplementedError(
                f"Model {model_cls} relation should be implemented now!"
            )

    return {group.varname: group for group in groups.values()}


def get_cookie_group(varname: str) -> CookieGroup | None:
    return all_cookie_groups().get(varname)


def get_cookie(cookie_group: CookieGroup, name: str, domain: str) -> Cookie | None:
    # loop over cookie set relation instead of doing a lookup query, as this should
    # come from the cache and avoid hitting the database
    return next(
        (
            cookie
            for cookie in cookie_group.cookies  # pyright: ignore[reportAttributeAccessIssue]
            if cookie.name == name and cookie.domain == domain
        ),
        None,
    )
