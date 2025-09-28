Django cookie consent
=====================

Manage cookie information and let visitors give or reject consent for them.

![License](https://img.shields.io/pypi/l/django-cookie-consent)
[![Build status][badge:GithubActions:CI]][GithubActions:CI]
[![Code Quality][badge:GithubActions:CQ]][GithubActions:CQ]
[![Code style: ruff][badge:ruff]][ruff]
[![Test coverage][badge:codecov]][codecov]
[![Documentation][badge:docs]][docs]

![Supported python versions](https://img.shields.io/pypi/pyversions/django-cookie-consent)
![Supported Django versions](https://img.shields.io/pypi/djversions/django-cookie-consent)
[![PyPI version][badge:pypi]][pypi]
[![NPM version][badge:npm]][npm]

**Features**

* cookies and cookie groups are stored in models for easy management
  through Django admin interface
* support for both opt-in and opt-out cookie consent schemes
* removing declined cookies (or non accepted when opt-in scheme is used)
* logging user actions when they accept and decline various cookies
* easy adding new cookies and seamlessly re-asking for consent for new cookies

Documentation
-------------

The documentation is hosted on [readthedocs][docs] and contains all instructions
to get started.

Alternatively, if the documentation is not available, you can consult or build the docs
from the `docs` directory in this repository.

[GithubActions:CI]: https://github.com/django-commons/django-cookie-consent/actions?query=workflow%3A%22Run+CI%22
[badge:GithubActions:CI]: https://github.com/django-commons/django-cookie-consent/workflows/Run%20CI/badge.svg
[GithubActions:CQ]: https://github.com/django-commons/django-cookie-consent/actions?query=workflow%3A%22Code+quality+checks%22
[badge:GithubActions:CQ]: https://github.com/django-commons/django-cookie-consent/workflows/Code%20quality%20checks/badge.svg
[ruff]: https://github.com/astral-sh/ruff
[badge:ruff]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[codecov]: https://codecov.io/gh/django-commons/django-cookie-consent
[badge:codecov]: https://codecov.io/gh/django-commons/django-cookie-consent/branch/master/graph/badge.svg
[docs]: https://django-cookie-consent.readthedocs.io/en/latest/?badge=latest
[badge:docs]: https://readthedocs.org/projects/django-cookie-consent/badge/?version=latest
[pypi]: https://pypi.org/project/django-cookie-consent/
[badge:pypi]: https://img.shields.io/pypi/v/django-cookie-consent.svg
[npm]: https://www.npmjs.com/package/django-cookie-consent
[badge:npm]: https://img.shields.io/npm/v/django-cookie-consent
