# Copyright: See the LICENSE file.

import collections
import datetime

import random
import unittest
from unittest import mock

import faker.providers
from faker.exceptions import UniquenessException

import factory


class MockUniqueProxy:

    def __init__(self, expected):
        self.expected = expected
        self.random = random.Random()

    def format(self, provider, **kwargs):
        return "unique {}".format(self.expected[provider])


class MockFaker:
    def __init__(self, expected):
        self.expected = expected
        self.random = random.Random()

    def format(self, provider, **kwargs):
        return self.expected[provider]

    @property
    def unique(self):
        return MockUniqueProxy(self.expected)


class AdvancedMockFaker:
    def __init__(self, handlers):
        self.handlers = handlers
        self.random = random.Random()

    def format(self, provider, **kwargs):
        handler = self.handlers[provider]
        return handler(**kwargs)


class FakerTests(unittest.TestCase):
    def setUp(self):
        self._real_fakers = factory.Faker._FAKER_REGISTRY
        factory.Faker._FAKER_REGISTRY = {}

    def tearDown(self):
        factory.Faker._FAKER_REGISTRY = self._real_fakers

    def _setup_mock_faker(self, locale=None, **definitions):
        if locale is None:
            locale = factory.Faker._DEFAULT_LOCALE
        factory.Faker._FAKER_REGISTRY[locale] = MockFaker(definitions)

    def _setup_advanced_mock_faker(self, locale=None, **handlers):
        if locale is None:
            locale = factory.Faker._DEFAULT_LOCALE
        factory.Faker._FAKER_REGISTRY[locale] = AdvancedMockFaker(handlers)

    def test_simple_biased(self):
        self._setup_mock_faker(name="John Doe")
        faker_field = factory.Faker('name')
        self.assertEqual("John Doe", faker_field.evaluate(None, None, {'locale': None}))

    def test_full_factory(self):
        class Profile:
            def __init__(self, first_name, last_name, email):
                self.first_name = first_name
                self.last_name = last_name
                self.email = email

        class ProfileFactory(factory.Factory):
            class Meta:
                model = Profile
            first_name = factory.Faker('first_name')
            last_name = factory.Faker('last_name', locale='fr_FR')
            email = factory.Faker('email')

        self._setup_mock_faker(first_name="John", last_name="Doe", email="john.doe@example.org")
        self._setup_mock_faker(first_name="Jean", last_name="Valjean", email="jvaljean@exemple.fr", locale='fr_FR')

        profile = ProfileFactory()
        self.assertEqual("John", profile.first_name)
        self.assertEqual("Valjean", profile.last_name)
        self.assertEqual('john.doe@example.org', profile.email)

    def test_override_locale(self):
        class Profile:
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name

        class ProfileFactory(factory.Factory):
            class Meta:
                model = Profile

            first_name = factory.Faker('first_name')
            last_name = factory.Faker('last_name', locale='fr_FR')

        self._setup_mock_faker(first_name="John", last_name="Doe")
        self._setup_mock_faker(first_name="Jean", last_name="Valjean", locale='fr_FR')
        self._setup_mock_faker(first_name="Johannes", last_name="Brahms", locale='de_DE')

        profile = ProfileFactory()
        self.assertEqual("John", profile.first_name)
        self.assertEqual("Valjean", profile.last_name)

        with factory.Faker.override_default_locale('de_DE'):
            profile = ProfileFactory()
            self.assertEqual("Johannes", profile.first_name)
            self.assertEqual("Valjean", profile.last_name)

        profile = ProfileFactory()
        self.assertEqual("John", profile.first_name)
        self.assertEqual("Valjean", profile.last_name)

    def test_add_provider(self):
        class Face:
            def __init__(self, smiley, french_smiley):
                self.smiley = smiley
                self.french_smiley = french_smiley

        class FaceFactory(factory.Factory):
            class Meta:
                model = Face

            smiley = factory.Faker('smiley')
            french_smiley = factory.Faker('smiley', locale='fr_FR')

        class SmileyProvider(faker.providers.BaseProvider):
            def smiley(self):
                return ':)'

        class FrenchSmileyProvider(faker.providers.BaseProvider):
            def smiley(self):
                return '(:'

        factory.Faker.add_provider(SmileyProvider)
        factory.Faker.add_provider(FrenchSmileyProvider, 'fr_FR')

        face = FaceFactory()
        self.assertEqual(":)", face.smiley)
        self.assertEqual("(:", face.french_smiley)

    def test_faker_customization(self):
        """Factory declarations in Faker parameters should be accepted."""
        Trip = collections.namedtuple('Trip', ['departure', 'transfer', 'arrival'])

        may_4th = datetime.date(1977, 5, 4)
        may_25th = datetime.date(1977, 5, 25)
        october_19th = datetime.date(1977, 10, 19)

        class TripFactory(factory.Factory):
            class Meta:
                model = Trip

            departure = may_4th
            arrival = may_25th
            transfer = factory.Faker(
                'date_between_dates',
                start_date=factory.SelfAttribute('..departure'),
                end_date=factory.SelfAttribute('..arrival'),
            )

        def fake_select_date(start_date, end_date):
            """Fake date_between_dates."""
            # Ensure that dates have been transferred from the factory
            # to Faker parameters.
            self.assertEqual(start_date, may_4th)
            self.assertEqual(end_date, may_25th)
            return october_19th

        self._setup_advanced_mock_faker(
            date_between_dates=fake_select_date,
        )

        trip = TripFactory()
        self.assertEqual(may_4th, trip.departure)
        self.assertEqual(october_19th, trip.transfer)
        self.assertEqual(may_25th, trip.arrival)

    def test_faker_unique(self):
        self._setup_mock_faker(name="John Doe", unique=True)
        with mock.patch("factory.faker.faker_lib.Faker") as faker_mock:
            faker_mock.return_value = MockFaker(dict(name="John Doe"))
            faker_field = factory.Faker('name', unique=True)
            self.assertEqual(
                "unique John Doe",
                faker_field.generate({'locale': None, 'unique': True})
            )


class RealFakerTest(unittest.TestCase):

    def test_faker_not_unique_not_raising_exception(self):
        faker_field = factory.Faker('pyint')
        # Make sure that without unique we can still create duplicated faker values.
        self.assertEqual(1, faker_field.generate({'locale': None, 'min_value': 1, 'max_value': 1}))
        self.assertEqual(1, faker_field.generate({'locale': None, 'min_value': 1, 'max_value': 1}))

    def test_faker_unique_raising_exception(self):
        faker_field = factory.Faker('pyint', min_value=1, max_value=1, unique=True)
        # Make sure creating duplicated values raises an exception on the second call
        # (which produces an identical value to the previous one).
        self.assertEqual(1, faker_field.generate({'locale': None, 'min_value': 1, 'max_value': 1, 'unique': True}))
        self.assertRaises(
            UniquenessException,
            faker_field.generate,
            {'locale': None, 'min_value': 1, 'max_value': 1, 'unique': True}
        )

    def test_faker_shared_faker_instance(self):
        class Foo:
            def __init__(self, val):
                self.val = val

        class Bar:
            def __init__(self, val):
                self.val = val

        class Factory1(factory.Factory):
            val = factory.Faker('pyint', min_value=1, max_value=1, unique=True)

            class Meta:
                model = Foo

        class Factory2(factory.Factory):
            val = factory.Faker('pyint', min_value=1, max_value=1, unique=True)

            class Meta:
                model = Bar

        f1 = Factory1.build()
        f2 = Factory2.build()
        self.assertEqual(f1.val, 1)
        self.assertEqual(f2.val, 1)

    def test_faker_inherited_faker_instance(self):
        class Foo:
            def __init__(self, val):
                self.val = val

        class Bar(Foo):
            def __init__(self, val):
                super().__init__(val)

        class Factory1(factory.Factory):
            val = factory.Faker('pyint', min_value=1, max_value=1, unique=True)

            class Meta:
                model = Foo

        class Factory2(Factory1):

            class Meta:
                model = Bar

        Factory1.build()
        with self.assertRaises(UniquenessException):
            Factory2.build()

    def test_faker_clear_unique_store(self):
        class Foo:
            def __init__(self, val):
                self.val = val

        class Factory1(factory.Factory):
            val = factory.Faker('pyint', min_value=1, max_value=1, unique=True)

            class Meta:
                model = Foo

        Factory1.build()
        Factory1.val.clear_unique_store()
        Factory1.build()
