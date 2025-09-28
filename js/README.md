# django-cookie-consent

Package containing the JS code for django-cookie-consent.

The cookiebar module is shipped in the Python package itself and available through
django's staticfiles mechanism. This package is aimed at users wishing to include the
assets in their own Javascript bundle through webpack/vite/...

[![PyPI version][badge:pypi]][pypi]

## Installation

```bash
npm install django-cookie-consent
```

You can now import the public API in your own bundle:

```ts
import {showCookieBar} from 'django-cookie-consent';
````

## TypeScript and ESM

The source code is written in TypeScript. The type declarations are shipped in the
published package.

We only publish ES modules and do not offer CommonJS.

## Building

Use ``nvm`` or your tool of choice to select the right NodeJS version:

```bash
nvm use
```

Building the NPM package:

```bash
npm run build
```

Lastly, the frontend toolchain also builds the cookiebar module bundle that's included
in the Python package:

```bash
npm run build:django-static
```

[pypi]: https://pypi.org/project/django-cookie-consent/
[badge:pypi]: https://img.shields.io/pypi/v/django-cookie-consent.svg
