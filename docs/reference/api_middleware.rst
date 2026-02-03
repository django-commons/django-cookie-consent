==========
Middleware
==========

CleanCookiesMiddleware
----------------------

.. code-block:: python

    MIDDLEWARE = [
        "cookie_consent.middleware.CleanCookiesMiddleware",
    ]


This middleware will automatically delete previously accepted first party cookies when
they are declined or not accepted/declined.

If you have enabled the ``COOKIE_CONSENT_OPT_OUT`` setting, then the cookies will only
be deleted if they are explicitly rejected.

.. note:: First party cookies are created by the host domain, while third party cookies
   are created by *other domains* than the one the user is visiting. For security
   reasons, browsers only allow your server to set first-party cookies.

   This gets even more confusing because third parties (such as analytics providers,
   ad-services...) DO set first party cookies rather than third-party, and store/read
   the information to then send it via another transport mechanism.

**Reference**

.. autoclass:: cookie_consent.middleware.CleanCookiesMiddleware
   :members:
