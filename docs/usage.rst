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

Both filters takes cookie group ``varname`` and optional cookie name with
domain. If cookie name with domain is used, the format is ``VARNAME=COOKIENAME:DOMAIN``.

Checking for 3rd party cookies dynamically
------------------------------------------

See :ref:`javascript_enable_scripts`.

.. versionremoved:: 1.0

    The ``js_type_for_cookie_consent`` tag was removed due to it relying on
    ``unsave-eval``. Instead, use the modern ``cookiebar.module.js`` and hook into
    the ``onAccept`` event and use ``template`` nodes.


Asking users for cookie consent in templates
--------------------------------------------

See :ref:`javascript`.
