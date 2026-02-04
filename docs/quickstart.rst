==========
Quickstart
==========

Installation
============

Install django-cookie-consent from PyPI with pip (recommended):

.. code-block:: bash

    pip install django-cookie-consent

Alternatively, you can install directly from Github:

.. code-block:: bash

    pip install git+https://github.com/django-commons/django-cookie-consent@main#egg=django-cookie-consent

.. warning:: Installing from the main branch can be unstable. It is recommended to pin
   your installation to a specific git tag or commit.

Configuration
=============

#. Add ``cookie_consent`` to your ``INSTALLED_APPS``.

#. Add ``django.template.context_processors.request``
   to ``TEMPLATE_CONTEXT_PROCESSORS`` if it is not already added.

#. Include django-cookie-consent urls in ``urls.py``

    .. code-block:: python

        from django.urls import path

        urlpatterns = [
            ...,
            path("cookies/", include("cookie_consent.urls")),
            ...,
        ]

#. Run the ``migrate`` management command to update your database tables:

    .. code-block:: bash

        python manage.py migrate
