===========
Example app
===========

The ``testapp`` project is both an example of how you could use this library and serves
as the reference for our test suite.

Running the testapp
-------------------

The testapp is essentially a standard django project, however there is no ``manage.py``
file. Instead, you have to use the ``django-admin`` command (``manage.py`` is only
a wrapper around this anyway).

#. First, clone the repository to get all the necessary files:

   .. code-block:: bash

       git clone https://github.com/django-commons/django-cookie-consent.git
       cd django-cookie-consent

#. Create a virtual environment for the project, using any supported Python version
   (3.10+) and activate it

   .. code-block:: bash

       python3.10 -m venv ./env
       source ./env/bin/activate

#. Install the application and dependencies

   .. code-block:: bash

       pip install .

#. Prepare your settings and local project instance

   .. code-block:: bash

       export DJANGO_SETTINGS_MODULE=testapp.settings PYTHONPATH=.
       django-admin migrate
       django-admin loaddata testapp/fixture.json
       django-admin createsuperuser

#. Start the development server

   .. code-block:: bash

       django-admin runserver

You can now navigate to ``http://127.0.0.1:8000`` and ``http://127.0.0.1:8000/admin/``.
