from django.urls import path

from .views import (
    CookieGroupAcceptView,
    CookieGroupDeclineView,
    CookieGroupListView,
    CookieStatusView,
)

urlpatterns = [
    path("accept/", CookieGroupAcceptView.as_view(), name="cookie_consent_accept"),
    path("decline/", CookieGroupDeclineView.as_view(), name="cookie_consent_decline"),
    path("status/", CookieStatusView.as_view(), name="cookie_consent_status"),
    path("", CookieGroupListView.as_view(), name="cookie_consent_cookie_group_list"),
]
