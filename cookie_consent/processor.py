from collections.abc import Collection
from typing import Literal

from django.http import HttpRequest, HttpResponseBase

from .conf import settings
from .models import ACTION_ACCEPTED, ACTION_DECLINED, CookieGroup, LogItem
from .util import get_cookie_dict_from_request, set_cookie_dict_to_response


class CookiesProcessor:
    """
    Process the accept/decline logic for cookie groups.
    """

    def __init__(self, request: HttpRequest, response: HttpResponseBase):
        self.request = request
        self.response = response

    def process(
        self,
        cookie_groups: Collection[CookieGroup],
        action: Literal["accept", "decline"],
    ) -> None:
        """
        Apply ``action`` to the specified ``cookie_groups``.

        Mutates the response by updating the cookie tracking the cookie group status. If
        there are no cookie groups provided, nothing happens.
        """
        if not cookie_groups:
            return

        cookie_dic = get_cookie_dict_from_request(self.request)

        match action:
            case "accept":
                for cookie_group in cookie_groups:
                    cookie_dic[cookie_group.varname] = cookie_group.get_version()
            case "decline":
                self._delete_cookies(cookie_groups)
                for cookie_group in cookie_groups:
                    cookie_dic[cookie_group.varname] = settings.COOKIE_CONSENT_DECLINE

        self._log_action(cookie_groups, action)
        set_cookie_dict_to_response(self.response, cookie_dic)

    def _log_action(
        self,
        cookie_groups: Collection[CookieGroup],
        action: Literal["accept", "decline"],
    ) -> None:
        if not settings.COOKIE_CONSENT_LOG_ENABLED:
            return
        # TODO: replace with stdlib logging call/helper instead of creating DB records
        # directly.

        action_map: dict[Literal["accept", "decline"], int] = {
            "accept": ACTION_ACCEPTED,
            "decline": ACTION_DECLINED,
        }
        log_items: list[LogItem] = [
            LogItem(
                action=action_map[action],
                cookiegroup=cookie_group,
                version=cookie_group.get_version(),
            )
            for cookie_group in cookie_groups
        ]
        LogItem.objects.bulk_create(log_items)

    def _delete_cookies(self, cookie_groups: Collection[CookieGroup]) -> None:
        for cookie_group in cookie_groups:
            if not cookie_group.is_deletable:
                continue
            for cookie in cookie_group.cookie_set.all():
                self.response.delete_cookie(cookie.name, cookie.path, cookie.domain)
