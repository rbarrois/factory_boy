# Copyright: See the LICENSE file.


"""Additional declarations for "faker" attributes.

Usage:

    class MyFactory(factory.Factory):
        class Meta:
            model = MyProfile

        first_name = factory.Faker('name')
"""


import contextlib
from typing import Dict

import faker
import faker.config

from . import declarations


class Faker(declarations.BaseDeclaration):
    """Wrapper for 'faker' values.

    Args:
        provider (str): the name of the Faker field
        locale (str): the locale to use for the faker
        unique (bool): whether generated values must be unique

        All other kwargs will be passed to the underlying provider
        (e.g ``factory.Faker('ean', length=10)``
        calls ``faker.Faker.ean(length=10)``)

    Usage:
        >>> foo = factory.Faker('name')
    """
    def __init__(self, provider, **kwargs):
        locale = kwargs.pop('locale', None)
        unique = kwargs.pop('unique', False)
        self.provider = provider
        super().__init__(
            locale=locale,
            unique=unique,
            **kwargs)

    def evaluate(self, instance, step, extra):
        locale = extra.pop('locale')
        unique = extra.pop('unique')
        subfaker = self._get_faker(locale, unique)
        return subfaker.format(self.provider, **extra)

    _FAKER_REGISTRY: Dict[str, faker.Faker] = {}
    _DEFAULT_LOCALE = faker.config.DEFAULT_LOCALE

    @classmethod
    @contextlib.contextmanager
    def override_default_locale(cls, locale):
        old_locale = cls._DEFAULT_LOCALE
        cls._DEFAULT_LOCALE = locale
        try:
            yield
        finally:
            cls._DEFAULT_LOCALE = old_locale

    @classmethod
    def _get_faker(cls, locale=None, unique=False):
        if locale is None:
            locale = cls._DEFAULT_LOCALE

        cache_key = f"{locale}_{unique}"
        if cache_key not in cls._FAKER_REGISTRY:
            subfaker = faker.Faker(locale=locale)
            if unique:
                subfaker = subfaker.unique
            cls._FAKER_REGISTRY[cache_key] = subfaker

        return cls._FAKER_REGISTRY[cache_key]

    @classmethod
    def add_provider(cls, provider, locale=None):
        """Add a new Faker provider for the specified locale"""
        cls._get_faker(locale, True).add_provider(provider)
        cls._get_faker(locale, False).add_provider(provider)
