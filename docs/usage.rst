=====
Usage
=====

Managing cookie groups and cookies
----------------------------------

Typically you manage the cookie groups and associated cookies through the admin
interface. You can of course integrate your own user interface if you prefer.

Cache invalidation is wired up at the model layer.

Checking for cookie consent in templates
----------------------------------------

django-cookie-consent provides some :ref:`template tags and filters <api_templatetags>`.
Most notable, you'll want to use:

.. currentmodule:: cookie_consent.templatetags.cookie_consent_tags

* :func:`cookie_group_accepted`
* :func:`cookie_group_declined`

to test whether a cookie group and/or specific cookie have been accepted or declined.

For example:

.. code-block:: django

  {% load cookie_consent_tags %}
  {% if request|cookie_group_accepted:"analytics" %}
    {# load 3rd party analytics #}
  {% endif %}

  {% if request|cookie_group_accepted:"analytics=_ga:example.com" %}
    {# load google analytics #}
  {% endif %}

Both filters takes the cookie group ``varname`` and an optional cookie name with
domain. If the cookie name with domain is used, the format is
``VARNAME=COOKIENAME:DOMAIN``.

Asking users for cookie consent in templates
--------------------------------------------

See :ref:`javascript`.

Checking for cookie consent in Python code
------------------------------------------

.. currentmodule:: cookie_consent.util

You can use the :func:`get_cookie_value_from_request` utility function to check consent
status in views and other Python code. This function powers the template filters from
above.

.. code-block:: python

    from cookie_consent.util import get_cookie_value_from_request

    def myview(request, *args, **kwargs):
        cc = get_cookie_value_from_request(request, "mycookies")
        if cc:
            # add cookie

You can check if a particular cookie in the group is accepted:

.. code-block:: python

    cc = get_cookie_value_from_request(request, "mycookies", "mycookie1:example.com")


Checking for 3rd party cookies dynamically
------------------------------------------

See :ref:`javascript_enable_scripts`.

.. versionremoved:: 1.0

    The ``js_type_for_cookie_consent`` tag was removed due to its reliance on
    ``unsave-eval`` (`MDN <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src#unsafe_eval_expressions>`_).
    Instead, use the modern ``cookiebar.module.js`` and hook into the ``onAccept`` event
    and use ``template`` nodes.
