=====
Usage
=====

Checking for cookie consent in views
------------------------------------

.. code-block:: python

  from cookie_consent.util import get_cookie_value_from_request

  def myview(request, *args, **kwargs):
    cc = get_cookie_value_from_request(request, "mycookies")
    if cc:
      # add cookie

Checking if specific cookie in Cookie group is accepted is possible:

.. code-block:: python

    cc = get_cookie_value_from_request(request, "mycookies", "mycookie1")

Checking for cookie consent in templates
----------------------------------------

Use ``cookie_group_accepted`` or ``cookie_group_declined`` template filters.

.. code-block:: django

  {% load cookie_consent_tags %}
  {% if request|cookie_group_accepted:"analytics" %}
    {# load 3rd party analytics #}
  {% endif %}

Bot filters takes cookie group ``varname`` and optional cookie name with
domain. If cookie name with domain is used, format is 
``VARNAME=COOKIENAME:DOMAIN``.


Checking for 3rd party cookies dynamically
------------------------------------------

.. warning::

    .. deprecated:: 0.5.0

    This approach does not work well with page-level caches and (strict) content
    security policies. Instead, use the new :ref:`Javascript <javascript>` approach
    with ``<template>`` nodes.

Using ``js_type_for_cookie_consent`` templatetag for script type attribute
would set ``x/cookie_consent`` thus making browser skip executing this block
of javascript code.

When consent for using specific cookies is given, code can be evaluated
without reloading page.

.. code-block:: django

  {% load cookie_consent_tags %}
  <script type="{% js_type_for_cookie_consent request "social" "*:.google.com" %}" data-varname="social">
    alert("Social cookie accepted");
  </script>


Asking users for cookie consent in templates
--------------------------------------------

See :ref:`javascript`.
