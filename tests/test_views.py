from collections.abc import Collection

from django.test import Client
from django.urls import reverse

import pytest
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from cookie_consent.models import (
    ACTION_ACCEPTED,
    ACTION_DECLINED,
    Cookie,
    CookieGroup,
    LogItem,
)


@pytest.mark.django_db
def test_cookiegroup_list_view(client: Client, optional_cookiegroup: CookieGroup):
    response = client.get(reverse("cookie_consent_cookie_group_list"))

    assert response.status_code == 200
    assertTemplateUsed("cookie_consent/cookiegroup_list.html")
    assertContains(response, '<input type="submit" value="Accept">')
    assertContains(response, '<input type="submit" value="Decline">')


def assertAcceptedCookieGroups(client: Client, varnames: Collection[str]):
    cookie_status = client.get(reverse("cookie_consent_status")).json()
    assert set(cookie_status["acceptedCookieGroups"]) == set(varnames)


def assertDeclinedCookieGroups(client: Client, varnames: Collection[str]):
    cookie_status = client.get(reverse("cookie_consent_status")).json()
    assert set(cookie_status["declinedCookieGroups"]) == set(varnames)


@pytest.mark.parametrize(
    "next_param,expected_url",
    (
        (reverse("test_page"), reverse("test_page")),
        ("https://evil.com", "/fallback/"),
    ),
)
@pytest.mark.django_db
def test_processing_get_success_url(
    client: Client, settings, next_param: str, expected_url: str
):
    """
    Assert that the ``?next`` query param is used and sanitized.

    Redirects to other hosts are unsafe and a fallback is expected instead.
    """
    settings.COOKIE_CONSENT_SUCCESS_URL = "/fallback/"

    response = client.post(
        reverse("cookie_consent_accept"),
        data={"all_groups": "true", "next": next_param},
    )

    assertRedirects(response, expected_url, fetch_redirect_response=False)


@pytest.mark.django_db
def test_alternative_redirect_fallback(client: Client, settings):
    settings.COOKIE_CONSENT_SUCCESS_URL = "/alternative"

    response = client.post(
        reverse("cookie_consent_accept"),
        data={"all_groups": "true"},
    )

    assertRedirects(response, "/alternative", fetch_redirect_response=False)


@pytest.mark.django_db
def test_accept_multiple_cookiegroups_submitted_via_post_body(client: Client):
    cookie_group_1 = CookieGroup.objects.create(varname="group_1", name="Optional 1")
    Cookie.objects.create(cookiegroup=cookie_group_1, name="foo")
    cookie_group_2 = CookieGroup.objects.create(varname="group_2", name="Optional 2")
    Cookie.objects.create(cookiegroup=cookie_group_2, name="bar")
    cookie_group_3 = CookieGroup.objects.create(varname="group_3", name="Optional 3")
    Cookie.objects.create(cookiegroup=cookie_group_3, name="baz")
    body = {
        "all_groups": "false",
        "cookie_groups": ["group_1", "group_2"],
    }

    response = client.post(reverse("cookie_consent_accept"), data=body)

    assertAcceptedCookieGroups(client, {"group_1", "group_2"})
    assertRedirects(response, expected_url="/cookies/")


@pytest.mark.django_db
def test_accept_all_cookiegroups(client: Client, optional_cookiegroup: CookieGroup):
    response = client.post(
        reverse("cookie_consent_accept"), data={"all_groups": "true"}
    )

    assertRedirects(
        response,
        reverse("cookie_consent_cookie_group_list"),
        fetch_redirect_response=False,
    )
    assertAcceptedCookieGroups(client, {"optional"})


@pytest.mark.django_db
def test_accept_cookie_view_ajax(client: Client, optional_cookiegroup: CookieGroup):
    response = client.post(
        reverse("cookie_consent_accept"),
        data={"cookie_groups": "optional"},
        headers={"x-requested-with": "XMLHttpRequest"},
    )

    assert response.status_code == 200
    assert response.content == b""


@pytest.mark.django_db
def test_accept_cookie_invalid_varname(
    client: Client, optional_cookiegroup: CookieGroup
):
    assert optional_cookiegroup.varname != "missing"

    response = client.post(
        reverse("cookie_consent_accept"), data={"cookie_groups": "missing"}
    )

    assert response.status_code == 200
    assertContains(response, "Select a valid choice")


@pytest.mark.django_db
def test_ajax_like_accept_cookie_invalid_varname(
    client: Client, optional_cookiegroup: CookieGroup
):
    assert optional_cookiegroup.varname != "missing"

    response = client.post(
        reverse("cookie_consent_accept"),
        data={"cookie_groups": "missing"},
        headers={"x-cookie-consent-fetch": "1"},
    )

    assert response.status_code == 200
    errors = response.json()
    assert "cookie_groups" in errors
    assert errors["cookie_groups"][0]["code"] == "invalid_choice"


@pytest.mark.django_db
def test_decline_multiple_cookiegroups_submitted_via_post_body(client: Client):
    cookie_group_1 = CookieGroup.objects.create(varname="group_1", name="Optional 1")
    Cookie.objects.create(cookiegroup=cookie_group_1, name="foo")
    cookie_group_2 = CookieGroup.objects.create(varname="group_2", name="Optional 2")
    Cookie.objects.create(cookiegroup=cookie_group_2, name="bar")
    cookie_group_3 = CookieGroup.objects.create(varname="group_3", name="Optional 3")
    Cookie.objects.create(cookiegroup=cookie_group_3, name="baz")
    body = {
        "all_groups": "false",
        "cookie_groups": ["group_1", "group_2"],
    }

    response = client.post(reverse("cookie_consent_decline"), data=body)

    assertDeclinedCookieGroups(client, {"group_1", "group_2"})
    assertRedirects(response, expected_url="/cookies/")


@pytest.mark.django_db
def test_decline_all_cookiegroups(client: Client, optional_cookiegroup: CookieGroup):
    response = client.post(
        reverse("cookie_consent_decline"), data={"all_groups": "true"}
    )

    assertRedirects(
        response,
        reverse("cookie_consent_cookie_group_list"),
        fetch_redirect_response=False,
    )
    assertDeclinedCookieGroups(client, {"optional"})


@pytest.mark.django_db
def test_decline_cookie_view_ajax(client: Client, optional_cookiegroup: CookieGroup):
    response = client.post(
        reverse("cookie_consent_decline"),
        data={"cookie_groups": "optional"},
        headers={"x-requested-with": "XMLHttpRequest"},
    )

    assert response.status_code == 200
    assert response.content == b""


@pytest.mark.django_db
def test_decline_cookie_invalid_varname(
    client: Client, optional_cookiegroup: CookieGroup
):
    assert optional_cookiegroup.varname != "missing"

    response = client.post(
        reverse("cookie_consent_decline"), data={"cookie_groups": "missing"}
    )

    assert response.status_code == 200
    assertContains(response, "Select a valid choice")


@pytest.mark.django_db
def test_ajax_like_decline_cookie_invalid_varname(
    client: Client, optional_cookiegroup: CookieGroup
):
    assert optional_cookiegroup.varname != "missing"

    response = client.post(
        reverse("cookie_consent_decline"),
        data={"cookie_groups": "missing"},
        headers={"x-cookie-consent-fetch": "1"},
    )

    assert response.status_code == 200
    errors = response.json()
    assert "cookie_groups" in errors
    assert errors["cookie_groups"][0]["code"] == "invalid_choice"


@pytest.mark.django_db
def test_logging_enabled(client: Client, optional_cookiegroup: CookieGroup):
    # accept and decline should each produce a log item
    client.post(reverse("cookie_consent_accept"), data={"cookie_groups": "optional"})
    client.post(reverse("cookie_consent_decline"), data={"cookie_groups": "optional"})

    log_items = LogItem.objects.all()

    assert len(log_items) == 2

    accept_log_item = next(item for item in log_items if item.action == ACTION_ACCEPTED)
    assert accept_log_item.cookiegroup == optional_cookiegroup
    assert accept_log_item.version == optional_cookiegroup.get_version()

    decline_log_item = next(
        item for item in log_items if item.action == ACTION_DECLINED
    )
    assert decline_log_item.cookiegroup == optional_cookiegroup
    assert decline_log_item.version == optional_cookiegroup.get_version()


@pytest.mark.django_db
def test_logging_disabled(client: Client, optional_cookiegroup: CookieGroup, settings):
    settings.COOKIE_CONSENT_LOG_ENABLED = False
    # accept and decline should each produce a log item
    client.post(reverse("cookie_consent_accept"), data={"cookie_groups": "optional"})
    client.post(reverse("cookie_consent_decline"), data={"cookie_groups": "optional"})

    assert not LogItem.objects.exists()


@pytest.mark.django_db
def test_integration_test_page_works(client: Client, optional_cookiegroup: CookieGroup):
    CookieGroup.objects.create(varname="social", name="Social")
    Cookie.objects.create(cookiegroup=optional_cookiegroup, name="optional_test_cookie")
    url = reverse("test_page")

    response = client.get(url)
    assertContains(response, '"optional" cookies not accepted or declined')

    # accept the optional group
    client.post(reverse("cookie_consent_accept"), data={"cookie_groups": "optional"})
    after_accept_response = client.get(url)
    assertContains(after_accept_response, '"optional" cookies accepted')
    assert (
        client.cookies["optional_test_cookie"].value
        == "optional cookie set from django"
    )

    # decline the optional group
    client.post(reverse("cookie_consent_decline"), data={"cookie_groups": "optional"})
    after_decline_response = client.get(url)
    assert client.cookies["optional_test_cookie"].value == ""
    assertContains(after_decline_response, '"optional" cookies declined')
