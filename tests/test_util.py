from datetime import datetime

from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from hypothesis import example, given, strategies as st

from cookie_consent.conf import settings
from cookie_consent.models import Cookie, CookieGroup
from cookie_consent.util import (
    dict_to_cookie_str,
    get_cookie_groups,
    get_cookie_value_from_request,
    is_cookie_consent_enabled,
    parse_cookie_str,
)


class UtilTest(TestCase):
    def setUp(self):
        self.cookie_group = CookieGroup.objects.create(
            varname="optional",
            name="Optional",
        )
        self.cookie = Cookie.objects.create(
            cookiegroup=self.cookie_group,
            name="foo",
        )
        self.factory = RequestFactory()
        self.request = self.factory.get("")

    def test_parse_cookie_str(self):
        cookie_str = "foo=2013-06-04T01:08:58.262162|bar=2013-06-04T01:08:58"
        res = parse_cookie_str(cookie_str)
        dic = {
            "foo": "2013-06-04T01:08:58.262162",
            "bar": "2013-06-04T01:08:58",
        }
        self.assertEqual(res, dic)

    def test_dict_to_cookie_str(self):
        cookie_str = "|"
        dic = {
            "foo": "2013-06-04T01:08:58.262162",
            "bar": "2013-06-04T01:08:58",
        }
        cookie_str = dict_to_cookie_str(dic)
        self.assertEqual(parse_cookie_str(cookie_str), dic)

    def test_get_cookie_value_from_request(self):
        cookie_str = dict_to_cookie_str({"optional": self.cookie_group.get_version()})
        self.request.COOKIES[settings.COOKIE_CONSENT_NAME] = cookie_str
        res = get_cookie_value_from_request(self.request, "optional")
        self.assertTrue(res)

    def test_get_cookie_value_from_request_declined(self):
        cookie_str = dict_to_cookie_str({"optional": datetime(1999, 1, 1).isoformat()})
        self.request.COOKIES[settings.COOKIE_CONSENT_NAME] = cookie_str
        res = get_cookie_value_from_request(self.request, "optional")
        self.assertFalse(res)

    def test_get_cookie_value_from_request_empty(self):
        res = get_cookie_value_from_request(self.request, "optional")
        self.assertIsNone(res)

    def test_get_cookie_value_from_request_added_cookies(self):
        cookie_str = dict_to_cookie_str(
            {
                "optional": self.cookie_group.get_version(),
            }
        )
        Cookie.objects.create(
            cookiegroup=self.cookie_group,
            name="bar",
            domain=".example.com",
        )
        self.request.COOKIES[settings.COOKIE_CONSENT_NAME] = cookie_str
        res = get_cookie_value_from_request(self.request, "optional")
        self.assertIsNone(res)

    def test_get_cookie_value_from_request_specific_cookie(self):
        cookie_str = dict_to_cookie_str({"optional": self.cookie_group.get_version()})
        self.request.COOKIES[settings.COOKIE_CONSENT_NAME] = cookie_str
        res = get_cookie_value_from_request(self.request, "optional", "foo:")
        self.assertTrue(res)

        Cookie.objects.create(
            cookiegroup=self.cookie_group,
            name="bar",
            domain=".example.com",
        )
        res = get_cookie_value_from_request(
            self.request, "optional", "bar:.example.com"
        )
        self.assertFalse(res)

        res = get_cookie_value_from_request(self.request, "optional", "foo:")
        self.assertTrue(res)

        cookie_str = dict_to_cookie_str({"optional": self.cookie_group.get_version()})
        self.request.COOKIES[settings.COOKIE_CONSENT_NAME] = cookie_str
        res = get_cookie_value_from_request(
            self.request, "optional", "bar:.example.com"
        )
        self.assertTrue(res)

    def test_is_cookie_consent_enabled(self):
        self.assertTrue(is_cookie_consent_enabled(None))

    @override_settings(COOKIE_CONSENT_ENABLED=lambda r: False)
    def test_is_cookie_consent_enabled_callable(self):
        self.assertFalse(is_cookie_consent_enabled(None))

    def test_get_cookie_groups(self):
        self.assertIn(self.cookie_group, get_cookie_groups("optional"))

        cookie_group2 = CookieGroup.objects.create(
            varname="foo",
            name="foo",
        )
        self.assertIn(self.cookie_group, get_cookie_groups("foo,optional"))
        self.assertIn(cookie_group2, get_cookie_groups("foo,optional"))


@example({"": "|"})
@example({"": "="})
@given(
    cookie_dict=st.dictionaries(
        keys=st.text(min_size=0),
        values=st.text(min_size=0),
    )
)
def test_serialize_and_parse_cookie_str(cookie_dict):
    serialized = dict_to_cookie_str(cookie_dict)
    parsed = parse_cookie_str(serialized)

    assert len(parsed.keys()) <= len(cookie_dict.keys())


@given(cookie_str=st.text(min_size=0))
def test_parse_cookie_str(cookie_str: str):
    parsed = parse_cookie_str(cookie_str)

    assert isinstance(parsed, dict)
