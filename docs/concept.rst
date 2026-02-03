=============
Main concepts
=============

Cookie Group
------------

The :class:`CookieGroup <cookie_consent.models.CookieGroup>` model represents a group
of related cookies. Cookie groups can be either required or not. Users can accept or
decline the use of the cookies in the non-required cookie groups.

Versions
^^^^^^^^

Each cookie group has a "current version" set to the timestamp of the last added
Cookie in it. When a user accepts a cookie group, the current version (at the time of
consent) is :ref:`saved <concept_storing_consent>`.

Versions allow django-cookie-consent to check if new cookies have been introduced after
the user has given consent for a cookie group, so that they can be prompted again to
accept the new cookie(s).

Important attributes:
^^^^^^^^^^^^^^^^^^^^^

``varname``
  The variable name that acts as unique identifier for the cookie group. You can use
  the value in template tags and filters to refer to a particular cookie group.

``is_required``
  Required cookies are never deleted and users cannot accept or decline them. For
  example, Django's default ``sessionid`` and ``csrftoken`` cookies are required for
  the correct functioning of your project. Without these cookies, the website will not
  work properly - so users can't opt-out.

``is_deletable``
  If a cookie group is marked as deletable, django-cookie-consent will try to delete
  the cookies in this group when the user declines the group, or through the
  :class:`cookie_consent.middleware.CleanCookiesMiddleware`.

Cookie
------

The :class:`Cookie<cookie_consent.models.Cookie>` model represents as single cookie.

.. admonition:: Domain and path
   :collapsible: closed

   The ``domain`` and ``path`` fields are important to be able to delete the
   cookies programmatically. Keep in mind that only cookies of your own domain can
   be deleted.

.. _concept_storing_consent:

Saving user selection
---------------------

A bit ironically, django-cookie-consent uses a cookie itself to store the user consent.
By default, the name ``cookie_consent`` is used.

An example value of such a cookie could be:

.. code-block:: none

    optional=-1|social=2013-06-04T03:17:01.421395Z

The meaning of this is:

* the user declined the cookie group with varname ``optional``
* the user accepted the cookie group with varname ``social``, and specifically only the
  cookies that were created before the stated timestamp

Caching
-------

django-cookie-consent keeps the non-required cookie groups and cookies in cache, to
avoid hitting the database for each request. By default, the ``default`` Django cache
is used. You can modify this, see :ref:`settings`.

.. note:: Django's default cache is a local-memory cache. Cache invalidation in one
   wsgi-server process will not propagate to other instances/processes, so you can
   temporarily see inconsistent results. It's recommended to use a shared cache like
   Redis/Valkey or Memcache.
