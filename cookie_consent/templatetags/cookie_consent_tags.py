import warnings

from django import template
from django.utils.html import json_script

from ..cache import all_cookie_groups as get_all_cookie_groups
from ..conf import settings
from ..util import (
    are_all_cookies_accepted,
    get_accepted_cookies,
    get_cookie_dict_from_request,
    get_cookie_string,
    get_cookie_value_from_request,
    get_not_accepted_or_declined_cookie_groups,
    is_cookie_consent_enabled,
)

register = template.Library()


@register.filter
def cookie_group_accepted(request, arg):
    """
    Filter returns if cookie group is accepted.

    Examples:
    ::

        {{ request|cookie_group_accepted:"analytics" }}
        {{ request|cookie_group_accepted:"analytics=*:.google.com" }}
    """
    value = get_cookie_value_from_request(request, *arg.split("="))
    return value is True


@register.filter
def cookie_group_declined(request, arg):
    """
    Filter returns if cookie group is declined.
    """
    value = get_cookie_value_from_request(request, *arg.split("="))
    return value is False


@register.filter
def all_cookies_accepted(request):
    """
    Filter returns if all cookies are accepted.
    """
    return are_all_cookies_accepted(request)


@register.simple_tag
def not_accepted_or_declined_cookie_groups(request):
    """
    Assignement tag returns cookie groups that does not yet given consent
    or decline.
    """
    return get_not_accepted_or_declined_cookie_groups(request)


@register.filter
def cookie_consent_enabled(request):
    """
    Filter returns if cookie consent enabled for this request.
    """
    return is_cookie_consent_enabled(request)


@register.simple_tag
def get_accept_cookie_groups_cookie_string(request, cookie_groups):  # pragma: no cover
    """
    Tag returns accept cookie string suitable to use in javascript.
    """
    warnings.warn(
        "Cookie string template tags for JS are deprecated and will be removed "
        "in django-cookie-consent 1.0",
        DeprecationWarning,
        stacklevel=1,
    )
    cookie_dic = get_cookie_dict_from_request(request)
    for cookie_group in cookie_groups:
        cookie_dic[cookie_group.varname] = cookie_group.get_version()
    return get_cookie_string(cookie_dic)


@register.simple_tag
def get_decline_cookie_groups_cookie_string(request, cookie_groups):
    """
    Tag returns decline cookie string suitable to use in javascript.
    """
    warnings.warn(
        "Cookie string template tags for JS are deprecated and will be removed "
        "in django-cookie-consent 1.0",
        DeprecationWarning,
        stacklevel=1,
    )
    cookie_dic = get_cookie_dict_from_request(request)
    for cookie_group in cookie_groups:
        cookie_dic[cookie_group.varname] = settings.COOKIE_CONSENT_DECLINE
    return get_cookie_string(cookie_dic)


@register.simple_tag
def js_type_for_cookie_consent(request, varname, cookie=None):
    """
    Tag returns "x/cookie_consent" when processing javascript
    will create an cookie and consent does not exists yet.

    Example::

      <script type="{% js_type_for_cookie_consent request "social" %}"
      data-varname="social">
        alert("Social cookie accepted");
      </script>
    """
    # This approach doesn't work with page caches and/or strict
    # Content-Security-Policies (unless you use nonces, which again doesn't work with
    # aggressive page caching).
    warnings.warn(
        "Template tags for use in/with JS are deprecated and will be removed "
        "in django-cookie-consent 1.0",
        DeprecationWarning,
        stacklevel=1,
    )
    enabled = is_cookie_consent_enabled(request)
    if not enabled:
        res = True
    else:
        value = get_cookie_value_from_request(request, varname, cookie)
        if value is None:
            res = settings.COOKIE_CONSENT_OPT_OUT
        else:
            res = value
    return "text/javascript" if res else "x/cookie_consent"


@register.filter
def accepted_cookies(request):
    """
    Filter returns accepted cookies varnames.

    .. code-block:: django

        {{ request|accepted_cookies }}

    """
    warnings.warn(
        "The 'accepted_cookies' template filter is deprecated and will be removed"
        "in django-cookie-consent 1.0.",
        DeprecationWarning,
        stacklevel=1,
    )
    return [c.varname for c in get_accepted_cookies(request)]


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
