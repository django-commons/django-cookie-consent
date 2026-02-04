from collections.abc import Callable

from django.http import HttpRequest, HttpResponseBase

from .cache import all_cookie_groups
from .conf import settings
from .util import get_cookie_dict_from_request, is_cookie_consent_enabled


def _should_delete_cookie(group_version: str | None) -> bool:
    # declined after it was accepted (and set) before
    if group_version == settings.COOKIE_CONSENT_DECLINE:
        return True

    # if you need to opt-out instead of opt-in, then we only delete the cookie in the
    # above scenario -> when the group is explicitly declined
    if settings.COOKIE_CONSENT_OPT_OUT:
        return False

    # when we are opt-in and have no information whether the cookie group was accepted
    # or declined, delete the cookie(s).
    if group_version is None:
        return True

    return False


class CleanCookiesMiddleware:
    """
    Clean declined or non-accepted cookies.

    Note that this only applies if COOKIE_CONSENT_OPT_OUT is not set.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        if is_cookie_consent_enabled(request):
            self.process_response(request, response)
        return response

    def process_response(self, request: HttpRequest, response: HttpResponseBase):
        cookie_dic = get_cookie_dict_from_request(request)

        cookies_to_delete = []
        for cookie_group in all_cookie_groups().values():
            if not cookie_group.is_deletable:
                continue

            group_version = cookie_dic.get(cookie_group.varname, None)
            for cookie in cookie_group.cookie_set.all():
                if cookie.name not in request.COOKIES:
                    continue
                if _should_delete_cookie(group_version):
                    cookies_to_delete.append(cookie)

        for cookie in cookies_to_delete:
            response.delete_cookie(cookie.name, cookie.path, cookie.domain)

        return response
