================
Migrating to 1.0
================

After more than 12 years since it's initial inception, django-cookie-consent finally
has a 1.0 version number. It means that the public API is stable, and breaking changes
will be reflected in a new major version number.

Some breaking changes compared to version 0.9 and earlier may affect you. This document
helps you upgrade from the earlier versions to 1.0.

Legacy cookiebar removal
========================

The largest breaking change is the removal of ``cookie_consent/cookiebar.js`` in favour
of the new ``cookie_consent/cookiebar.module.js``. It was deprecated in version 0.5.0b0.

Before
------

Before, you'd have code along the lines of:

.. code-block:: django

    {% load cookie_consent_tags %}

    <script type="text/javascript" src="{% static 'cookie_consent/cookiebar.js' %}"></script>

    <script type="{% js_type_for_cookie_consent request "analytics" "*:example.com" %}" data-varname="analytics">
      console.log('Analytics script activated.');
    </script>

    <script>
        showCookieBar({
          content: '<div class="cookie-bar"> <p>We use cookies to improve your browsing experience. By continuing to use our site, you agree to our use of cookies.</p> <a href="/accept_cookies" class="cc-cookie-accept">Accept</a> <a href="/decline_cookies" class="cc-cookie-decline">Decline</a> </div>',
          cookie_groups: ['analytics'],
          cookie_decline: '{% get_decline_cookie_groups_cookie_string request analytics %}',
          beforeDeclined: function () {
            console.log('User is about to decline cookies');
          },
        });
    </script>

Note the requirement of the ``cc-cookie-accept`` and ``cc-cookie-decline`` class names.

After
-----

.. code-block:: django

    {% load static cookie_consent_tags %}

    {% static "cookie_consent/cookiebar.module.js" as cookiebar_src %}
    {% url "cookie_consent_cookie_group_list" as url_cookies %}
    {% url 'cookie_consent_status' as status_url %}

    {% all_cookie_groups 'cookie-consent__cookie-groups' %}
    {# Emits a <script type="application/json" id="cookie-consent__cookie-groups">...</script> tag #}

    <template id="cookie-consent__cookie-bar">
        <div class="cookie-bar">
            <p>We use cookies to improve your browsing experience. By continuing to use
            our site, you agree to our use of cookies.</p>
            <a href="#" class="cc-cookie-accept">Accept</button>
            <a href="#" class="cc-cookie-decline">Decline</button>
        </div>
    </template>

    <template data-varname="analytics">
        <script>
          console.log('Analytics script activated.');
        </script>
    </template>

    <script type="module">
        import {showCookieBar} from '{{ cookiebar_src }}';
        showCookieBar({
          statusUrl: '{{ status_url|escapejs }}',
          templateSelector: '#cookie-consent__cookie-bar',
          cookieGroupsSelector: '#cookie-consent__cookie-groups',
          acceptSelector: '.cc-cookie-accept',
          declineSelector: '.cc-cookie-decline',
          onAccept: (acceptedGroups) => {
            document.querySelector('.cookie-bar').style.display = 'none';
            document.querySelector('body').classList.remove('with-cookie-bar');

            acceptedGroups
              .filter(group => ['analytics'].includes(group.varname))
              .forEach(group => {
                const scriptTemplate = document.querySelector(
                  `template[data-varname="${group.varname}"]`
                ).content;
                const scripts = templateNode.content.cloneNode(true);
                document.body.appendChild(scripts);
              })
            ;
          },
          onDecline: (declinedGroups) => {
            document.querySelector('.cookie-bar').style.display = 'none';
            document.querySelector('body').classList.remove('with-cookie-bar');

            console.log('User is about to decline cookies', declinedGroups);
          },
        });
    </script>

.. note::

    There is no replacement for the ``cookie_decline`` option, since the backend
    already results in the cookie being updated.

Removed template tags
---------------------

**Cookie string builders**

The tags below have been obsoleted due to the cookie not being updated in Javascript
any longer:

* ``get_accept_cookie_groups_cookie_string``
* ``get_decline_cookie_groups_cookie_string``

Instead, make an Ajax or Fetch call to the ``cookie_consent_accept`` or
``cookie_consent_decline`` views, e.g.:

.. code-block:: django

    {% url 'cookie_consent_accept' as accept_url %}

    {{ accept_url|json_script:'cc-accept-url' }}

.. code-block:: javascript

    const acceptUrl = JSON.parse(document.getElementById('cc-accept-url').content);

    const formData = new FormData();
    formData.append('cookie_groups', 'analytics');

    window.fetch(acceptUrl, {
      method: 'POST',
      body: formData,
      credentials: 'same-origin',
      headers: {
        'X-Cookie-Consent-Fetch': '1',
        'X-CSRFToken': csrftoken, // get this from the template or the status endpoint
      }
    });

The view response updates the cookie for the browser.

**Script tag helper**

Tag: ``js_type_for_cookie_consent``

Use the ``template`` approach to enable scripts without full page reloads, see above.

**Get accepted cookie varnames**

Tag: ``accepted_cookies``

This would cause view/page cache issues, as it outputs the cookie varnames for the
user.

Instead, use Javascript for dynamic cookie banner behaviour, ideally the new cookiebar
module which uses the ``cookie_consent_status`` endpoint under the hood.

Alternatively, you can write your own implementation and fetch the current cookie
consent status of the user through the ``cookie_consent_status`` view.

Accept/decline views now use form data and only support POST requests
=====================================================================

Before 1.0, the accept and decline URLs would (optionally) take a comma-separated
URL path variable for the cookie group varnames:

* ``.../accept/social,analytics/``
* ``.../decline/social,analytics/``

while the URLs without the varnames would imply that *all* cookie groups are being
accepted or declined.

Instead of using ``{% url 'cookie_consent_accept' varname='social,analytics' %}``, in 1.0, use proper form semantics instead:

.. code-block:: django

    <form action="{% url 'cookie_consent_accept' %}" method="post">
        {% csrf_token %}
        <input type="hidden" name="cookie_groups" value="social">
        <input type="hidden" name="cookie_groups" value="analytics">
        <button type="submit">Accept</button>
    </form>

or, to accept/decline all cookie groups, instead of
``{% url 'cookie_consent_accept_all' %}``:

.. code-block:: django

    <form action="{% url 'cookie_consent_accept' %}" method="post">
        {% csrf_token %}
        <input type="hidden" name="all_groups" value="true">
        <button type="submit">Accept all</button>
    </form>

.. warning:: The accept/decline views now **require** a CSRF token to be provided. The
   new cookiebar module already handles this.

.. warning:: The ``DELETE`` support to decline cookies is removed. Use ``POST`` instead.

Enable safety/strictness features
=================================

The legacy situation may have prevented you from applying some security hardening or
improvements in your project(s). Below, we point out some things that are possible now.

**Enable the httpOnly flag for cookie consent's own cookie**

Since the legacy Javascript that was writing directly to ``document.cookie`` is removed,
you can block access to this cookie from Javascript entirely now.

The default settings already enable this.

**Use a strict(er) Content-Security-Policy**

The legacy cookiebar required ``unsave-eval``, which is a serious weakening of
cross-site scripting protections. If you were using it because of django-cookie-consent,
you can now remove it after upgrading to the new cookiebar module.

**Site/view cache can be enabled**

By relying on ``template`` nodes, Javascript and JSON-based endpoints for the dynamic
per-user information, your main views/page templates can now be safely cached using
Django's cache framework without serving cookie consent information from the wrong
user.

The future
==========

Future major versions will primarily be caused by dropping support for old Python and/or
Django version, notably when those go end-of-life. The Python/Django backwards
compatibility has an excellent track record, so we don't expect big impacts from this.

One larger rework that is planned, is the overhaul of the cookie accept/decline
logging. This will likely be another major release, but we expect a smooth upgrade
path.
