=========
Changelog
=========

0.9.0 (2025-09-28)
------------------

Maintenance and bugfix release.

**💥 Breaking changes**

* Dropped support for Python 3.8 (end-of-life).
* Dropped support for Python 3.9 (soon end-of-life).

**New features**

* [#114] You can now customize the redirect behaviour after accepting/declining cookies,
  using the new ``COOKIE_CONSENT_SUCCESS_URL`` setting.
* The admin now displays a warning for cookie groups that have no cookies in them.

**Bugfixes**

* [#135] Make cookie parsing and serialization more robust.

**Project maintenance**

* Transferred the package from the jazzband Github organization to django-commons, and
  updated all community-related documents like the code of conduct.
* Updated the package metadata to latest format.
* Bumped minimum required setuptools version to build the package.
* Replaced black and isort with Ruff for linting and code-formatting duties.
* Improved the test suite.
* The PyPI and NPM packages are now automatically published with Trusted Publishing,
  enhancing supply-chain security.

0.8.0 (2025-05-30)
------------------

Small feature release

**New features**

* The Javascript (package) now exports some more utilities (#126).

**Project maintenance**

* Fixed some test flakiness.

0.7.0 (2025-04-26)
------------------

Bugfix and Django supported versions release.

**New features**

* Confirmed Python 3.13 support.
* Confirmed Django 5.1 and 5.2 support.

**Project maintenance**

* Fixed incorrect JS example in the documentation.
* Removed Django 5.0 from CI pipeline (it still works, but Django 5.0 is end of life).
* Upgraded esbuild for the Javascript module building.

0.6.0 (2024-05-10)
------------------

Feature release with improved JS support.

**💥 Breaking changes**

Some (database) unique constraints have been added to the model fields. If you have
duplicate values in those fields, the migrations will crash. You should check for
duplicates before upgrading, and fix those:

.. code-block:: py

    from django.db.models import Count
    from cookie_consent.models import CookieGroup, Cookie

    # duplicated cookie groups (by varname)
    CookieGroup.objects.values("varname").annotate(n=Count("varname")).filter(n__gt=1)
    # <QuerySet []>

    # duplicated cookies
    Cookie.objects.values("cookiegroup", "name", "domain").annotate(n=Count("id")).filter(n__gt=1)
    # <QuerySet []>

Additionally, support for unmaintained Django versions (3.2, 4.1) is dropped.

**New features**

* The JS for the cookiebar module is rewritten in TypeScript and published as an
  `npm package`_ for people wishing to integrate this functionality in their own
  frontend stack. ``cookie_consent/cookiebar.module.js`` is still in the Python package,
  and it's generated from the same source code.

* Added support for natural keys in dumpdata/loaddata management commands.

**Deprecations**

None.

**Bugfixes**

* Fixed cache not being cleared after queryset (bulk) update/deletes
* Swapped the order of ``onShow`` and ``doInsert`` in the cookiebar JS. ``onShow`` is
  now called after the cookiebar is inserted into the document.
* Added missing unique constraint to ``CookieGroup.varname`` field
* Added missing unique constraint on ``Cookie`` fields ``cookiegroup``, ``name`` and
  ``domain``.

**Project maintenance**

* Add missing templatetag instruction to docs
* Removed Django < 4.2 compatibility shims
* Formatted code with latest black version
* Dropped Django 3.2 & 4.1 from the supported versions
* Removed unused dependencies
* Bumped github actions to latest versions
* Updated to modern packaging tooling with ``pyproject.toml``

.. _npm package: https://www.npmjs.com/package/django-cookie-consent

0.5.0b0 (2023-09-24)
--------------------

A django-cookie-consent version to test the new Javascript integration.

You can install this using:

.. code-block:: bash

    pip install django-cookie-consent --pre

The new cookiebar JS uses a modern approach and should resolve issues with page caches
and Content Security Policies. Please try it out and report any issues or suggestion on
Github!

**Breaking changes**

None

**New features**

* Implemented ``cookie_consent/cookiebar.module.js`` as a new Javascript integration.
  Please review the updated documentation for usage instructions. (#15, #49, #99)

**Deprecations**

Deprecated functionality is scheduled for removal in django-cookie-consent 1.0.

* Deprecated ``cookie_consent/cookiebar.js`` and added an alias ``legacyShowCookieBar``.
  Existing users are advised to upgrade to the new module approach, or at the very
  least substitute ``showCookieBar`` with ``window.legacyShowCookieBar`` to better keep
  track of this deprecation.

* Deprecated template tags that build up cookie strings suitable for Javascript.

**Bugfixes**

None

**Project maintenance**

* Extensively documented the new cookiebar JS usage.
* Added Playwright for end-to-end testing (covers both the new and legacy cookie bar)
* Removed unnecessary ``smart_str`` usage - thanks @some1ataplace
* Test app and tests themselves are now excluded from coverage measuring for more a
  more accurate reflection of the coverage status.

0.4.0 (2023-06-11)
------------------

.. note::

    The 0.4.0 release mainly has had a project management overhaul. The project has
    transferred to the Jazzband organization. This release mostly focuses on Python/Django
    version compatibility and organization of tests, CI etc.

    Many thanks for people who reported bugs, and especially, your patience for getting
    this release on PyPI.


**Breaking changes**

* Dropped support for Django 2.2, 3.0, 3.1 and 4.0
* Dropped support for Python 3.6 and 3.7

These versions are (nearly) end-of-life and no longer supported by their upstream teams.

**New features**

* Implemented settings for cookie flags: SameSite, HttpOnly, Secure, domain (#27, #60,
  #36, #88)
* Added Dutch translations

**Bugfixes**

* Cache instance resolution is now lazy (#41)
* Fixed support for Django 4.1 (#73) - thanks @alahdal
* Fixed default settings being bytestrings (#24, #55, #69)
* Fixed the middleware to clean cookies (#13) - thanks @some1ataplace
* Fixed bug in JS ``beforeDeclined`` attribute

**Project maintenance**

* Transferred project to Jazzband (#38, #64, #75)
* Replaced Travis CI with Github Actions (#64, #75)
* Set up correct test matrix for python/django versions (#75)
* Code is now ``isort`` and ``black`` formatted (#75)
* Set up ``tox`` and ``pytest`` for testing (#64, #75)
* 'Removed' the example app - the ``testapp`` in the repository is still a good example
* Configured tbump for the release flow
* Confirmed support for Python 3.11 and Django 4.2
* Added explicit template tag tests (#39)

**Documentation**

Did some initial restructuring to make the docs easier to digest, more to come.

* Added documentation on how to contribute
* Corrected settings documentation (#53, #14)
* Documented ``cookiebar.js`` usage (#90) - thanks @MrCordeiro
* Added better contributor documentation and example app documentation based on the
  ``testapp`` in the repository.

0.3.1 (2022-02-17)
------------------

- Protect against open redirect after accepting cookies (#48)


0.3.0 (2021-12-08)
------------------

* support ranges from django 2.2 to 4.0 and python 3.6 to 3.9


0.2.6 (2020-06-17)
------------------

* fix: setup for python 2.7


0.2.5 (2020-06-17)
------------------

* chore: add package descriptions


0.2.4 (2020-06-17)
------------------

* Cookie Bar Choosing Decline Not Disappearing Right Away (#22)

* 📦 NEW: pt_BR (#23)

0.2.3 (2020-06-15)
------------------

* Update package classifiers


0.2.2 (2020-06-15)
------------------

* 8732949 Remove jquery (#20)


0.2.1 (2020-06-02)
------------------

* fix: Set max version for django-appconf (#18)

* fix: Views ignore 'next' url parameter (#12)

* Update configuration.rst


0.2.0 (2020-02-11)
------------------

* support ranges from django 1.9 to 3.0 and python 2.7 to 3.7 (JonHerr)

0.1.1
-----

* tweak admin

* Add accepted_cookies template filter

* Add varname property to Cookie model

* Add translation catalog

0.1.0
-----

* Initial release
