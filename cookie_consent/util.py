import logging
from collections.abc import Callable, Collection

from django.http import HttpRequest

from .cache import all_cookie_groups, get_cookie, get_cookie_group
from .conf import settings
from .models import CookieGroup

logger = logging.getLogger(__name__)

COOKIE_GROUP_SEP = "|"
KEY_VALUE_SEP = "="


def parse_cookie_str(cookie: str) -> dict[str, str]:
    if not cookie:
        return {}

    bits = cookie.split(COOKIE_GROUP_SEP)

    def _gen_pairs():
        for possible_pair in bits:
            parts = possible_pair.split(KEY_VALUE_SEP)
            if len(parts) == 2:
                yield parts
            else:
                logger.debug("cookie_value_discarded", extra={"value": possible_pair})

    return dict(_gen_pairs())


def _contains_invalid_characters(*inputs: str) -> bool:
    # = and | are special separators. They are unexpected characters in both
    # keys and values.
    for separator in (COOKIE_GROUP_SEP, KEY_VALUE_SEP):
        for value in inputs:
            if separator in value:
                logger.debug("skip_separator", extra={"value": value, "sep": separator})
                return True
    return False


def dict_to_cookie_str(dic) -> str:
    """
    Serialize a dictionary of cookie-group metadata to a string.

    The result is stored in a cookie itself. Note that the dictionary keys are expected
    to be cookie group ``varname`` fields, which are validated against a slug regex. The
    values are supposed to be ISO-8601 timestamps.

    Invalid key/value pairs are dropped.
    """

    def _gen_pairs():
        for key, value in dic.items():
            if _contains_invalid_characters(key, value):
                continue
            yield f"{key}={value}"

    return "|".join(_gen_pairs())


def get_cookie_dict_from_request(request):
    cookie_str = request.COOKIES.get(settings.COOKIE_CONSENT_NAME)
    return parse_cookie_str(cookie_str)


def set_cookie_dict_to_response(response, dic):
    response.set_cookie(
        settings.COOKIE_CONSENT_NAME,
        dict_to_cookie_str(dic),
        max_age=settings.COOKIE_CONSENT_MAX_AGE,
        domain=settings.COOKIE_CONSENT_DOMAIN,
        secure=settings.COOKIE_CONSENT_SECURE or None,
        httponly=settings.COOKIE_CONSENT_HTTPONLY or None,
        samesite=settings.COOKIE_CONSENT_SAMESITE,
    )


def get_cookie_value_from_request(request: HttpRequest, varname: str, cookie: str = ""):
    """
    Returns if cookie group or its specific cookie has been accepted.

    Returns True or False when cookie is accepted or declined or None
    if cookie is not set.
    """
    cookie_dic = get_cookie_dict_from_request(request)
    if not cookie_dic:
        return None

    cookie_group = get_cookie_group(varname=varname)
    if not cookie_group:
        return None
    if cookie:
        name, domain = cookie.split(":")
        cookie = get_cookie(cookie_group, name, domain)
    else:
        cookie = None

    version = cookie_dic.get(varname, None)

    if version == settings.COOKIE_CONSENT_DECLINE:
        return False
    if version is None:
        return None
    if not cookie:
        v = cookie_group.get_version()
    else:
        v = cookie.get_version()
    if version >= v:
        return True
    return None


def get_cookie_groups(varname: str = "") -> Collection[CookieGroup]:
    if not varname:
        return all_cookie_groups().values()
    keys = varname.split(",")
    return [g for k, g in all_cookie_groups().items() if k in keys]


def are_all_cookies_accepted(request):
    """
    Returns if all cookies are accepted.
    """
    return all(
        [
            get_cookie_value_from_request(request, cookie_group.varname)
            for cookie_group in get_cookie_groups()
        ]
    )


def _get_cookie_groups_by_state(request, state: bool | None):
    return [
        cookie_group
        for cookie_group in get_cookie_groups()
        if get_cookie_value_from_request(request, cookie_group.varname) is state
    ]


def get_not_accepted_or_declined_cookie_groups(request):
    """
    Returns all cookie groups that are neither accepted or declined.
    """
    return _get_cookie_groups_by_state(request, state=None)


def get_accepted_cookie_groups(request):
    """
    Returns all cookie groups that are accepted.
    """
    return _get_cookie_groups_by_state(request, state=True)


def get_declined_cookie_groups(request):
    """
    Returns all cookie groups that are declined.
    """
    return _get_cookie_groups_by_state(request, state=False)


def is_cookie_consent_enabled(request: HttpRequest) -> bool:
    """
    Returns if django-cookie-consent is enabled for given request.
    """
    enabled: bool | Callable[[HttpRequest], bool] = settings.COOKIE_CONSENT_ENABLED
    return enabled(request) if callable(enabled) else enabled
