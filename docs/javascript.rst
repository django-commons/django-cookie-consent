.. _javascript:

======================
Javascript integration
======================

Cookie consent supports "classic" pages where you submit the accept/decline form and
then it performs a full page reload. This strategy is simple and straight-forward, as
any dynamic scripts tied to the cookie groups are then automatically initialized.

However, this does not lead to the best user-experience. Consider a user filling out a
long form and half-way they decide to get rid of the "annoying cookie bar". Either
accepting or declining will make them lose their changes, providing a frustrating
experience.

Using the scripts we ship, you can provide a better user experience, at the cost of
more development work.

.. _showcookiebar_getting_started:

Getting started
===============

Requirements
------------

The new script is designed for modern Javascript and modern browsers. It should also
integrate with JS tooling like Webpack/Rollup/ESBuild... but we are not actively testing
this. Please let us know via Github issues what your issues and/or wishes are!

As such, the target browsers must support:

* ``<script type="module">`` OR you must process the source code with a compiler (like
  Babel_).
* ``window.fetch``
* ``async``/``await`` syntax OR use a compiler like Babel.
* ES2020 (features like optional chaining are used)

In your Django template
-----------------------

**Add a template element for your content**

The ``<template>`` node is cloned and injected in the configured location. For example:

.. code-block:: django

    {% url "cookie_consent_cookie_group_list" as url_cookies %}

    <template id="cookie-consent__cookie-bar">
        <div class="cookie-bar">
            This site uses cookies for better performance and user experience.
            Do you agree to use these cookies?
            {# Button is the more accessible role, but an anchor tag would also work #}
            <button type="button" class="cookie-consent__accept">Accept</button>
            <button type="button" class="cookie-consent__decline">Decline</button>
            <a href="{{ url_cookies }}">Cookies info</a>
        </div>
    </template>

This lets you, the developer, control the exact layout, styling and content of the
cookie notice.

.. note:: Avoid using (most) of the built in template tags if you want to use
   template/view caching. For more background information, see:
   :ref:`javascript_design_considerations`.

**Emit the cookie groups for the Javascript**

The cookiebar module needs to know which cookie groups exist to decide whether a bar
has to be shown at all. A template tag exists which emits this as JSON serialized
data (in a page-cache compatible manner):

.. code-block:: django

    {# Set up the data and template for dynamic JS cookie bar #}
    {% all_cookie_groups 'cookie-consent__cookie-groups' %}
    {# Emits a <script type="application/json" id="cookie-consent__cookie-groups">...</script> tag #}

**Include a script that calls the showCookieBar function**

The most straight-forward way is to include this in your Django template:

.. code-block:: django

    {% load static cookie_consent_tags %}
    {% static "cookie_consent/cookiebar.module.js" as cookiebar_src %}
    {% url 'cookie_consent_status' as status_url %}
    <script type="module">
        import {showCookieBar} from '{{ cookiebar_src }}';
        showCookieBar({
          statusUrl: '{{ status_url|escapejs }}',
          templateSelector: '#cookie-consent__cookie-bar',
          cookieGroupsSelector: '#cookie-consent__cookie-groups',
          onShow: () => document.querySelector('body').classList.add('with-cookie-bar'),
          onAccept: () => document.querySelector('body').classList.remove('with-cookie-bar'),
          onDecline: () => document.querySelector('body').classList.remove('with-cookie-bar'),
        });
    </script>

You call the function with the necessary options, and on page-load the cookie bar will
be properly initialized.

The ``status_url`` is special - it points to a backend view which returns the
user-specific cookie consent status, returning the appropriate accept and decline URLs
and other details relevant to cookie consent.

.. note::

    If you prefer the include the cookiebar module in your own Javascript entrypoint,
    the easiest way is to install our `published package`_.

    This package should work with TypeScript, Webpack, ESBuild, Vite... and other popular
    bundlers and toolchains.

    Just be careful to install the same (minor) version as the backend package to avoid
    weird bugs.

.. _published package: hhttps://www.npmjs.com/package/django-cookie-consent

Options
=======

The ``showCookieBar`` function takes a few required options and many optional options to
tweak the behaviour to your wishes.

**Required options**

* ``statusUrl``: URL to the ``CookieStatusView`` - essential to determine the
  accept/decline URLs and CSRF token. Use ``{% url 'cookie_consent_status' as status_url %}``
  for the correct value, irrespective of your urlconf.

**Recommended options**

These options have default values, but to prevent surprises and maximum flexibility, you
should provide them. Please check the source code for their default values.

* ``templateSelector`` - CSS selector to find the template element of the cookie bar.
  This element will be cloned and ultimately added to the page.

* ``cookieGroupsSelector`` - CSS selector to the element produced by
  ``{% all_cookie_groups 'cookie-consent__cookie-groups' %}``. This provides all
  configured cookie groups in a JSON script tag and is read by ``showCookieBar`` to
  determine if a bar should be shown at all (e.g. if there are no cookie groups,
  nothing is done).

* ``acceptSelector`` - CSS selector to the element to accept all cookies. A ``click``
  event listener is bound to this element to register the cookies accept action.

* ``declineSelector`` - CSS selector to the element to decline all cookies. A ``click``
  event listener is bound to this element to register the cookies decline action.

**Optional**

* ``insertBefore`` - A CSS selector, DOM node or ``null``. If provided, the cookie bar
  is prepended before this node, otherwise it is appended to the body element.

* ``onShow`` - an optional callback function, called right before the cookie bar is
  added to the document.

* ``onAccept`` - an optional callback, called when the "cookies accept" element is
  clicked and when the cookie status is initially loaded. It receives the list of
  all cookie groups that are (now) accepted and the click event (if there was one).

* ``onDecline`` - an optional callback, called when the "cookies decline" element is
  clicked and when the cookie status is initially loaded. It receives the list of
  all cookie groups that are (now) declined and the click event (if there was one).

* ``csrfHeaderName`` - HTTP header name for the CSRF Token. Defaults to Django's default
  value, so if you have a non-default ``settings.CSRF_HEADER_NAME``, you must provide
  this.

.. _javascript_enable_scripts:

Enabling other scripts after cookies were accepted
==================================================

The legacy version of ``showCookieBar`` supported emitting scripts with a custom type
in the Django templates, which where then changed to ``type="text/javascript"`` to make
them execute without a full page reload. The new version does not support this out of
the box, as it may interfere with page caches, Content Security Policies and was poorly
documented.

We recommend hooking into the ``onAccept`` and ``onDecline`` hooks to perform these
actions.

E.g. in the django template:

.. code-block:: django

    <template id="analytics-scripts">
        <script type="text/javascript">
            // lots of interesting code
        </script>
        <script type="module" src="..."></script>
    </template>

and the Javascript function:

.. code-block:: javascript

    function onAccept(cookieGroups) {
        const analyticsEnabled = cookieGroups.find(group => group.varname === 'analytics') != undefined;
        if (analyticsEnabled) {
            const template = document.getElementById('analytics-scripts').content;
            const analyticsScripts = templateNode.content.cloneNode(true);
            document.body.appendChild(analyticsScripts);
        }
    }

Passing this ``onAccept`` callback then adds the scripts after the user accepted the
cookies, causing them to execute. This way, there's no reliance on ``unsafe-eval``.

.. _javascript_design_considerations:

Considerations and design decisions made for the JS integration
===============================================================

We realize there is quite a bit of work to do to use this functionality. We've aimed for
a trade-off where the simple things are easy to do and the complex set-ups are
achievable.

The :ref:`showcookiebar_getting_started` section should be close to plug-and-play by
integrating well with Django's static files. Especially on modern browsers, we intend
to have a working solution without intricate Javascript knowledge.

For more advanced Javascript usage/developers, we expose hooks and options to tap into
the life-cycle. The code may also serve as a reference for your own implementation.

HttpOnly and CSRF
-----------------

The cookie-consent cookie itself can safely be set to ``HttpOnly`` so it cannot be
tampered with (or even read) from Javascript. This follows security best practices. The
new script no longer touches ``document.cookie``.

Accepting and declining cookies must be CSRF-protected and use ``POST`` requests. This
works out of the box with the async calls we make - the status endpoint provides the
CSRF token to the Javascript so that it can include this via an HTTP header.

This means that you can mark your CSRF cookies ``HttpOnly`` in Django.

Content Security Policy (CSP)
-----------------------------

Content Security Policies aim to lock down which scripts, styles... can run in the
browser. They are a good tool in helping prevent Cross-Site-Scripting attacks, by
specifying from which sources scripts are allowed to run and usually by blocking
``eval`` (which should be the bare minimum of what you block).

The new scripts play well with this - you can include your analytics scripts inside
``<template>`` nodes and inject them dynamically without resorting to ``eval``.
Additionally, they are held against the configured CSP. Including these in the template
also provide the option to set a ``nonce`` (e.g. when using django-csp).

For more advanced setups, it's even possible a nonce is injected by a reverse proxy -
with creative Javascript you can read this nonce (typically from a ``<meta>`` tag) and
included it in the scripts you add in the ``onAccept`` hook.

Page caches
-----------

You should now be able to use Django's page cache which caches the entire response for
a given URL. The new script fetches the user-specific cookie status via an async call
which bypasses the cache (or you configure it to ``Vary`` on the cookies).

Localization
------------

The template element approach allows you to use Django's built in translation machinery,
keeping your templates readable and properly HTML-escaped.

Hooks
-----

The ``onShow``, ``onAccept`` and ``onDecline`` hooks allow you to perform additional
actions on the main events. You can add your own markup and Javascript for more advanced
user experiences.

.. _Babel: https://babeljs.io/
