from typing import Literal

from django.conf import settings
from django.urls import reverse_lazy
from django.utils.functional import Promise

from appconf import AppConf

__all__ = ["settings"]


class CookieConsentConf(AppConf):
    # django-cookie-consent cookie settings that store the configuration
    NAME: str = "cookie_consent"
    # TODO: rename to AGE for parity with django settings
    MAX_AGE: int = 60 * 60 * 24 * 365 * 1  # 1 year,
    DOMAIN: str | None = None
    SECURE: bool = False
    HTTPONLY: bool = True
    SAMESITE: Literal["Strict", "Lax", "None", False] = "Lax"

    DECLINE: str = "-1"

    ENABLED: bool = True

    OPT_OUT: bool = False

    CACHE_BACKEND: str = "default"

    LOG_ENABLED: bool = True
    """
    DeprecationWarning: in future versions the default may switch to log disabled.
    """

    SUCCESS_URL: str | Promise = reverse_lazy("cookie_consent_cookie_group_list")
