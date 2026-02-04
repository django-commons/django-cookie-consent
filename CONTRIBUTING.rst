By contributing you agree to abide by the
`Contributor Code of Conduct <https://github.com/django-commons/membership/blob/main/CODE_OF_CONDUCT.md>`_.

How can you contribute?
=======================

Contributions in all forms are welcome, not only code patches. You can contribute by:

* reporting bugs/issues
* triaging reported issues
* improving the documentation
* suggesting enhancements

Of course, if you report a bug or have a feature request, a pull request implementing
the fix or feature is much appreciated.

Contributing code
-----------------

If you decide to submit a patch or implement a feature, please adhere to the quality
checks:

* Pull requests must be accompanied by tests. We use ``pytest`` and prefer using this
  testing style over Django's ``django.test.TestCase``.
* Ideally, documentation updates are included in a pull request.
* Code formatting and linting is done with ``ruff``. There are tox environments and CI
  checks in place to check/enforce this.
* Follow Django's code style where possible.
* Keep commits atomic - one commit should only concern one topic. Bugfixes typically
  have one commit for the regression test and one commit with the fix.

Setting up the project for local development
--------------------------------------------

After checking out the project (through ``git clone``), it's advised to set up a
virtualenv with the lowest supported python and Django version.

You can then install the project with all the dev-tools:

.. code-block:: bash

   pip install -e .[tests,docs,release]

Some frontend tooling is needed too:

* NodeJS (for the version, see ``.nvmrc``, you can use ``nvm``)

.. code-block:: bash

    cd js
    nvm use
    npm install
    npm run build:django-static
    npm run build  # optional, but a nice check

**Running the testapp as dev environment**

In Django project's, you are typically expecting a ``manage.py`` file. This is less
common in libraries, but it's fairly straightforward to emulate this:

.. code-block:: bash

    export DJANGO_SETTINGS_MODULE=testapp.settings PYTHONPATH=.

    django-admin migrate
    django-admin createsuperuser
    django-admin runserver

You can now start working on your contribution!

**Running the tests**

Run the tests locally using ``tox`` to verify everything is okay:

.. code-block:: bash

   tox

Cheat sheet
-----------

This cheat sheet provides some quick tooling/commands lookup while working on the
project.

**Running tests**

In your current environment

.. code-block:: bash

   pytest

or to build the full test matrix

.. code-block:: bash

   tox

**Formatting the code for check-in**

.. code-block:: bash

   ruff format .
   ruff check --fix .

Should be sufficient. Consider using a pre-commit hook to automate this.

**Building the docs**

.. code-block:: bash

   cd docs
   make html

You can now open the file ``_build/html/index.html`` in your browser.

**Generating message catalogs**

.. code-block:: bash

    export DJANGO_SETTINGS_MODULE=testapp.settings
    cd cookie_consent
    django-admin makemessages --all
    cd ..

After translating the message, you need to compile the message catalogs:

.. code-block:: bash

    django-admin compilemessages

**Bumping the version/releasing**

After updating changelogs etc.

.. code-block:: bash

    tbump {new-version} --only-patch
    cd js
    npm version major|minor|patch --no-git-tag-version
    cd ..

    git commit -am ":bookmark: Bump to version <X.Y.Z>"

    git tag -s X.Y.Z
    git push origin main --tags
