# Copyright: See the LICENSE file.

"""Settings for factory_boy/Django tests."""

import os

FACTORY_ROOT = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),     # /path/to/fboy/tests/djapp/
    os.pardir,                                      # /path/to/fboy/tests/
    os.pardir,                                      # /path/to/fboy
)

MEDIA_ROOT = os.path.join(FACTORY_ROOT, 'tmp_test')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
    'replica': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}


INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'tests.djapp',
]

MIDDLEWARE_CLASSES = ()

SECRET_KEY = 'testing.'

# TODO: Will be the default after Django 5.0. Remove this setting when
# Django 5.0 is the last supported version.
USE_TZ = True
