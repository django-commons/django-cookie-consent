from collections.abc import Collection

from django import template
from django.http import HttpRequest
from django.utils.html import json_script

from ..cache import all_cookie_groups as get_all_cookie_groups
from ..models import CookieGroup
from ..util import (
    are_all_cookies_accepted,
    get_cookie_value_from_request,
    get_not_accepted_or_declined_cookie_groups,
    is_cookie_consent_enabled,
)

register = template.Library()


@register.filter
def cookie_group_accepted(request: HttpRequest, group_or_cookie: str) -> bool:
    """
    Return ``True`` if the cookie group/cookie is accepted.

    Examples:

    .. code-block:: django

        {{ request|cookie_group_accepted:"analytics" }}
        {{ request|cookie_group_accepted:"analytics=*:.google.com" }}
    """
    value = get_cookie_value_from_request(request, *group_or_cookie.split("="))
    return value is True


@register.filter
def cookie_group_declined(request: HttpRequest, group_or_cookie: str) -> bool:
    """
    Return ``True`` if the cookie group/cookie is declined.

    Examples:

    .. code-block:: django

        {{ request|cookie_group_declined:"analytics" }}
        {{ request|cookie_group_declined:"analytics=*:.google.com" }}
    """
    value = get_cookie_value_from_request(request, *group_or_cookie.split("="))
    return value is False


@register.filter
def all_cookies_accepted(request: HttpRequest) -> bool:
    """
    Filter returns if all cookies are accepted.
    """
    return are_all_cookies_accepted(request)


@register.simple_tag
def not_accepted_or_declined_cookie_groups(
    request: HttpRequest,
) -> Collection[CookieGroup]:
    """
    Return the cookie groups for which no explicit accept or decline has been given.
    """
    return get_not_accepted_or_declined_cookie_groups(request)


@register.filter
def cookie_consent_enabled(request: HttpRequest) -> bool:
    """
    Indicate whether the cookie-consent app is enabled or not.
    """
    return is_cookie_consent_enabled(request)


@register.simple_tag
def all_cookie_groups(element_id: str):
    """
    Serialize all cookie groups to JSON and output them in a script tag.

    :param element_id: The ID for the script tag so you can look it up in JS later.

    This uses Django's core json_script filter under the hood.
    """
    groups = get_all_cookie_groups()
    value = [group.for_json() for group in groups.values()]
    return json_script(value, element_id)
