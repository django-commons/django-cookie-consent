from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.urls import reverse

from cookie_consent.cache import delete_cache
from cookie_consent.models import Cookie, CookieGroup

factory = RequestFactory()


@override_settings(COOKIE_CONSENT_OPT_OUT=False)
class CleanCookiesMiddlewareTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.cookie_group = CookieGroup.objects.create(
            varname="optional",
            name="Optional (test) cookies",
        )
        cls.cookie = Cookie.objects.create(
            cookiegroup=cls.cookie_group,
            name="optional_test_cookie",
            domain="127.0.0.1",
            path="/",
        )

    def setUp(self):
        super().setUp()
        self.addCleanup(delete_cache)

    def _accept_and_set_cookie(self):
        with self.subTest("initial setup"):
            # ensure we start with cookies first being accepted
            endpoint = reverse("cookie_consent_accept")

            consent_response = self.client.post(
                endpoint,
                data={"cookie_groups": ["optional"]},
                follow=True,
                headers={"x-requested-with": "XMLHttpRequest"},
            )
            self.assertEqual(consent_response.status_code, 200)

            # hit the test page to set the cookie
            self.client.get(reverse("test_page"))
            self.assertIn("optional_test_cookie", self.client.cookies)

    def assertCookieDeleted(self, name: str):
        if name not in self.client.cookies:
            self.fail(
                "Cookie not present in client cookies, which is required to delete it"
            )

        # deleting a cookie is done by setting the expiry date to the past/max-age 0
        # so that the browser effectively is instructed to delete the cookie
        cookie = self.client.cookies[name]
        cookie_dict = dict(cookie)
        self.assertEqual(cookie_dict["max-age"], 0)
        self.assertIn("1970", cookie_dict["expires"])
        self.assertEqual(cookie.value, "")

    def test_middleware_decline_previously_accepted_cookiegroup_cookies_are_deleted(
        self,
    ):
        self._accept_and_set_cookie()

        with self.subTest("decline prevously accepted group"):
            url = reverse("cookie_consent_decline")

            decline_response = self.client.post(
                url, data={"cookie_groups": ["optional"]}, follow=True
            )

            self.assertEqual(decline_response.status_code, 200)

        # fetch the test page and assert the middleware deleted the cookie
        self.client.get(reverse("test_page"))

        self.assertCookieDeleted("optional_test_cookie")

    def test_middleware_no_cookie_consent_cookie_present_cookies_are_deleted(self):
        self._accept_and_set_cookie()
        # Delete cookie_consent cookie
        del self.client.cookies["cookie_consent"]

        # fetch the test page and assert the middleware deleted the cookie
        self.client.get(reverse("test_page"))

        # Check if cookie_consent cookie is deleted
        self.assertCookieDeleted("optional_test_cookie")

    def test_cookie_consent_disabled(self):
        self._accept_and_set_cookie()

        with override_settings(COOKIE_CONSENT_ENABLED=False):
            self.client.get(reverse("test_page"))

        cookie = self.client.cookies["optional_test_cookie"]
        self.assertEqual(cookie.value, "optional cookie set from django")

    def test_cookie_group_not_deletable(self):
        self.cookie_group.is_deletable = False
        self.cookie_group.save()
        self._accept_and_set_cookie()

        self.client.get(reverse("test_page"))

        cookie = self.client.cookies["optional_test_cookie"]
        self.assertEqual(cookie.value, "optional cookie set from django")

    @override_settings(COOKIE_CONSENT_OPT_OUT=True)
    def test_with_opt_out_behaviour(self):
        # set the cookie
        self.client.get(reverse("test_page"), {"force": "1"})

        # call view to run middleware
        self.client.get(reverse("test_page"))

        cookie = self.client.cookies["optional_test_cookie"]
        self.assertEqual(cookie.value, "optional cookie set from django")
