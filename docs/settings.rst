.. _settings:

========
Settings
========

The cookie settings (name, max-age, domain...) follow the same principles like
Django's built-in session cookie. For more details, please check that documenation
for more details about the meaning.

``COOKIE_CONSENT_NAME``
  name of consent cookie that remembers user choice

  Default: ``cookie_consent``.

``COOKIE_CONSENT_MAX_AGE``
  max-age of consent cookie, in seconds

  Default: 1 year

``COOKIE_CONSENT_DOMAIN``
  Domain to restrict the cookie to.

  Default: ``None``

``COOKIE_CONSENT_SECURE``
  Whether to only set the cookie in an HTTPS context.

  Default: ``False``

``COOKIE_CONSENT_HTTPONLY``
  Whether access from Javascript is blocked.

  Default: ``True``

``COOKIE_CONSENT_SAMESITE``
  The SameSite policy. Possible values are ``"Strict"``, ``"Lax"``, ``"None"`` or
  ``False`` to disable setting the flag.

  Default: ``"Lax"``

``COOKIE_CONSENT_DECLINE``
  decline value

  Default: ``-1``

``COOKIE_CONSENT_ENABLED``
  boolean or callable that receives request and returns a boolean.

  For example, if you want to enable cookie consent for debug or staff only:

  .. code-block:: python

      COOKIE_CONSENT_ENABLED = lambda r: DEBUG or (r.user.is_authenticated and r.user.is_staff)

  Default: ``True``

``COOKIE_CONSENT_OPT_OUT``
  Boolean value represents if cookies are opt-in (``False``) or opt-out (``True``).
  Opt-out cookies are set until declined.
  Opt-in cookies are set only if accepted.

  Default: ``False``

``COOKIE_CONSENT_CACHE_BACKEND``
  Alias for backend to use for caching.

  Default: ``default``

``COOKIE_CONSENT_LOG_ENABLED``
  Boolean value represents if the accept/decline user actions will be logged to the
  database. Turning it off might be useful for preventing your database from getting
  filled up with log items.

  Default: ``True`` 

``COOKIE_CONSENT_SUCCESS_URL``
  The success URL to redirect the user to after a successful accept/decline action. If
  a ``?next`` parameter is present in the request, then it takes priority over this
  setting.

  Default: the URL of the built-in cookie list view.
