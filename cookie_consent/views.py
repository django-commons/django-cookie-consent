from typing import Literal

from django.contrib.auth.views import RedirectURLMixin
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
    JsonResponse,
)
from django.middleware.csrf import get_token as get_csrf_token
from django.urls import reverse
from django.views.generic import ListView, View

from .conf import settings
from .forms import ProcessCookiesForm
from .models import CookieGroup
from .processor import CookiesProcessor
from .util import (
    get_accepted_cookie_groups,
    get_declined_cookie_groups,
    get_not_accepted_or_declined_cookie_groups,
)


def is_ajax_like(request: HttpRequest) -> bool:
    # legacy ajax, removed in Django 4.0 (used to be request.is_ajax())
    ajax_header = request.headers.get("X-Requested-With")
    if ajax_header == "XMLHttpRequest":
        return True

    # module-js uses fetch and a custom header
    return bool(request.headers.get("X-Cookie-Consent-Fetch"))


class CookieGroupListView(ListView):
    """
    Display all cookies.
    """

    model = CookieGroup


class CookieGroupBaseProcessView(RedirectURLMixin, View):
    """
    Process the cookie groups submitted in the POST request (or URL parameters).

    :class:`RedirectURLMixin` takes care of the hardening against open redirects.
    """

    cookie_process_action: Literal["accept", "decline"]
    """
    Processing action to apply, must be set on the subclasses.
    """

    def get_default_redirect_url(self) -> str:
        return settings.COOKIE_CONSENT_SUCCESS_URL

    def post(self, request: HttpRequest, *args, **kwargs):
        form = ProcessCookiesForm(data=request.POST)

        if not form.is_valid():
            if is_ajax_like(request):
                return JsonResponse(form.errors.get_json_data())
            else:
                return HttpResponse(form.errors.render())

        cookie_groups = form.get_cookie_groups()

        response: HttpResponseBase
        if is_ajax_like(request):
            response = HttpResponse()
        else:
            response = HttpResponseRedirect(self.get_success_url())

        processor = CookiesProcessor(request, response)
        processor.process(cookie_groups, action=self.cookie_process_action)

        return response


class CookieGroupAcceptView(CookieGroupBaseProcessView):
    """
    View to accept CookieGroup.
    """

    cookie_process_action = "accept"


class CookieGroupDeclineView(CookieGroupBaseProcessView):
    """
    View to decline CookieGroup.
    """

    cookie_process_action = "decline"

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class CookieStatusView(View):
    """
    Check the current accept/decline status for cookies.

    The returned accept and decline URLs are specific to this user and include the
    cookie groups that weren't accepted or declined yet.

    Note that this endpoint also returns a CSRF Token to be used by the frontend,
    as baking a CSRFToken into a cached page will not reliably work.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        accepted = get_accepted_cookie_groups(request)
        declined = get_declined_cookie_groups(request)
        not_accepted_or_declined = get_not_accepted_or_declined_cookie_groups(request)
        data = {
            "csrftoken": get_csrf_token(request),
            "acceptUrl": reverse("cookie_consent_accept"),
            "declineUrl": reverse("cookie_consent_decline"),
            "acceptedCookieGroups": [group.varname for group in accepted],
            "declinedCookieGroups": [group.varname for group in declined],
            "notAcceptedOrDeclinedCookieGroups": [
                group.varname for group in not_accepted_or_declined
            ],
        }
        return JsonResponse(data)
