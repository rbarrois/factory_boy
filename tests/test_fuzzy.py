# Copyright: See the LICENSE file.


import datetime
import decimal
import unittest
import warnings
from unittest import mock

from factory import fuzzy, random

from . import utils


class FuzzyAttributeTestCase(unittest.TestCase):
    def test_simple_call(self):
        d = fuzzy.FuzzyAttribute(lambda: 10)

        res = utils.evaluate_declaration(d)
        self.assertEqual(10, res)

        res = utils.evaluate_declaration(d)
        self.assertEqual(10, res)


class FuzzyChoiceTestCase(unittest.TestCase):
    def test_unbiased(self):
        options = [1, 2, 3]
        d = fuzzy.FuzzyChoice(options)
        res = utils.evaluate_declaration(d)
        self.assertIn(res, options)

    def test_mock(self):
        options = [1, 2, 3]
        fake_choice = lambda d: sum(d)

        d = fuzzy.FuzzyChoice(options)

        with mock.patch('factory.random.randgen.choice', fake_choice):
            res = utils.evaluate_declaration(d)

        self.assertEqual(6, res)

    def test_generator(self):
        def options():
            yield from range(3)

        d = fuzzy.FuzzyChoice(options())

        res = utils.evaluate_declaration(d)
        self.assertIn(res, [0, 1, 2])

        # And repeat
        res = utils.evaluate_declaration(d)
        self.assertIn(res, [0, 1, 2])

    def test_lazy_generator(self):
        class Gen:
            def __init__(self, options):
                self.options = options
                self.unrolled = False

            def __iter__(self):
                self.unrolled = True
                return iter(self.options)

        opts = Gen([1, 2, 3])
        d = fuzzy.FuzzyChoice(opts)
        self.assertFalse(opts.unrolled)

        res = utils.evaluate_declaration(d)
        self.assertIn(res, [1, 2, 3])
        self.assertTrue(opts.unrolled)

    def test_getter(self):
        options = [('a', 1), ('b', 2), ('c', 3)]
        d = fuzzy.FuzzyChoice(options, getter=lambda x: x[1])
        res = utils.evaluate_declaration(d)
        self.assertIn(res, [1, 2, 3])


class FuzzyIntegerTestCase(unittest.TestCase):
    def test_definition(self):
        """Tests all ways of defining a FuzzyInteger."""
        fuzz = fuzzy.FuzzyInteger(2, 3)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertIn(res, [2, 3])

        fuzz = fuzzy.FuzzyInteger(4)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertIn(res, [0, 1, 2, 3, 4])

    def test_biased(self):
        fake_randrange = lambda low, high, step: (low + high) * step

        fuzz = fuzzy.FuzzyInteger(2, 8)

        with mock.patch('factory.random.randgen.randrange', fake_randrange):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual((2 + 8 + 1) * 1, res)

    def test_biased_high_only(self):
        fake_randrange = lambda low, high, step: (low + high) * step

        fuzz = fuzzy.FuzzyInteger(8)

        with mock.patch('factory.random.randgen.randrange', fake_randrange):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual((0 + 8 + 1) * 1, res)

    def test_biased_with_step(self):
        fake_randrange = lambda low, high, step: (low + high) * step

        fuzz = fuzzy.FuzzyInteger(5, 8, 3)

        with mock.patch('factory.random.randgen.randrange', fake_randrange):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual((5 + 8 + 1) * 3, res)


class FuzzyDecimalTestCase(unittest.TestCase):
    def test_definition(self):
        """Tests all ways of defining a FuzzyDecimal."""
        fuzz = fuzzy.FuzzyDecimal(2.0, 3.0)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(
                decimal.Decimal('2.0') <= res <= decimal.Decimal('3.0'),
                "value %d is not between 2.0 and 3.0" % res,
            )

        fuzz = fuzzy.FuzzyDecimal(4.0)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(
                decimal.Decimal('0.0') <= res <= decimal.Decimal('4.0'),
                "value %d is not between 0.0 and 4.0" % res,
            )

        fuzz = fuzzy.FuzzyDecimal(1.0, 4.0, precision=5)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(
                decimal.Decimal('1.0') <= res <= decimal.Decimal('4.0'),
                "value %d is not between 1.0 and 4.0" % res,
            )
            self.assertTrue(res.as_tuple().exponent, -5)

    def test_biased(self):
        fake_uniform = lambda low, high: low + high

        fuzz = fuzzy.FuzzyDecimal(2.0, 8.0)

        with mock.patch('factory.random.randgen.uniform', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(decimal.Decimal('10.0'), res)

    def test_biased_high_only(self):
        fake_uniform = lambda low, high: low + high

        fuzz = fuzzy.FuzzyDecimal(8.0)

        with mock.patch('factory.random.randgen.uniform', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(decimal.Decimal('8.0'), res)

    def test_precision(self):
        fake_uniform = lambda low, high: low + high + 0.001

        fuzz = fuzzy.FuzzyDecimal(8.0, precision=3)

        with mock.patch('factory.random.randgen.uniform', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(decimal.Decimal('8.001').quantize(decimal.Decimal(10) ** -3), res)

    def test_no_approximation(self):
        """We should not go through floats in our fuzzy calls unless actually needed."""
        fuzz = fuzzy.FuzzyDecimal(0, 10)

        decimal_context = decimal.getcontext()
        old_traps = decimal_context.traps[decimal.FloatOperation]
        try:
            decimal_context.traps[decimal.FloatOperation] = True
            utils.evaluate_declaration(fuzz)
        finally:
            decimal_context.traps[decimal.FloatOperation] = old_traps

    def test_decimal_args(self):
        low = decimal.Decimal('5.5')
        high = decimal.Decimal('10')
        fuzz = fuzzy.FuzzyDecimal(low, high)

        with self.assertRaises(TypeError):
            utils.evaluate_declaration(fuzz)


class FuzzyDecimalDecTestCase(unittest.TestCase):
    def test_definition(self):
        """Tests all ways of defining a FuzzyDecimal."""
        fuzz = fuzzy.FuzzyDecimalDec('2.0', decimal.Decimal('3.0'))
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(
                decimal.Decimal('2.0') <= res <= decimal.Decimal('3.0'),
                "value %d is not between 2.0 and 3.0" % res,
            )

        fuzz = fuzzy.FuzzyDecimalDec(4.0)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(
                decimal.Decimal('0.0') <= res <= decimal.Decimal('4.0'),
                "value %d is not between 0.0 and 4.0" % res,
            )

        fuzz = fuzzy.FuzzyDecimalDec(1.0, '4.0', precision=5)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(
                decimal.Decimal('1.0') <= res <= decimal.Decimal('4.0'),
                "value %d is not between 1.0 and 4.0" % res,
            )
            self.assertTrue(res.as_tuple().exponent, -5)

    def test_biased(self):
        fake_uniform = lambda low, high: low + high

        fuzz = fuzzy.FuzzyDecimalDec(decimal.Decimal('2.0'), decimal.Decimal('8.0'))

        with mock.patch('factory.random.uniform_decimal', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(decimal.Decimal('10.0'), res)
        fuzz = fuzzy.FuzzyDecimalDec('2.0', '8.0')

        with mock.patch('factory.random.uniform_decimal', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(decimal.Decimal('10.0'), res)

        fuzz = fuzzy.FuzzyDecimalDec(3.33, 20 / 3, precision=2)

        with mock.patch('factory.random.uniform_decimal', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(decimal.Decimal('10.00'), res)

    def test_biased_high_only(self):
        fake_uniform = lambda low, high: low + high

        fuzz = fuzzy.FuzzyDecimalDec('8.0')

        with mock.patch('factory.random.uniform_decimal', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(decimal.Decimal('8.0'), res)

    def test_precision(self):
        fake_uniform = lambda low, high: low + high + decimal.Decimal('0.001')

        fuzz = fuzzy.FuzzyDecimalDec('8.0', precision=3)

        with mock.patch('factory.random.uniform_decimal', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(decimal.Decimal('8.001').quantize(decimal.Decimal(10) ** -3), res)

    def test_decimal_args(self):
        low = decimal.Decimal('5.5')
        high = decimal.Decimal('10')
        fuzz = fuzzy.FuzzyDecimalDec(low, high)

        res = utils.evaluate_declaration(fuzz)
        self.assertTrue(low <= res <= high, "value %d is not between 5.5 and 10" % res)


class FuzzyFloatTestCase(unittest.TestCase):
    def test_definition(self):
        """Tests all ways of defining a FuzzyFloat."""
        fuzz = fuzzy.FuzzyFloat(2.0, 3.0)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(2.0 <= res <= 3.0, "value %d is not between 2.0 and 3.0" % res)

        fuzz = fuzzy.FuzzyFloat(4.0)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(0.0 <= res <= 4.0, "value %d is not between 0.0 and 4.0" % res)

        fuzz = fuzzy.FuzzyDecimal(1.0, 4.0, precision=5)
        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertTrue(1.0 <= res <= 4.0, "value %d is not between 1.0 and 4.0" % res)
            self.assertTrue(res.as_tuple().exponent, -5)

    def test_biased(self):
        fake_uniform = lambda low, high: low + high

        fuzz = fuzzy.FuzzyFloat(2.0, 8.0)

        with mock.patch('factory.random.randgen.uniform', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(10.0, res)

    def test_biased_high_only(self):
        fake_uniform = lambda low, high: low + high

        fuzz = fuzzy.FuzzyFloat(8.0)

        with mock.patch('factory.random.randgen.uniform', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(8.0, res)

    def test_default_precision(self):
        fake_uniform = lambda low, high: low + high + 0.000000000000011

        fuzz = fuzzy.FuzzyFloat(8.0)

        with mock.patch('factory.random.randgen.uniform', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(8.00000000000001, res)

    def test_precision(self):
        fake_uniform = lambda low, high: low + high + 0.001

        fuzz = fuzzy.FuzzyFloat(8.0, precision=4)

        with mock.patch('factory.random.randgen.uniform', fake_uniform):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(8.001, res)


class FuzzyDateTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup useful constants
        cls.jan1 = datetime.date(2013, 1, 1)
        cls.jan3 = datetime.date(2013, 1, 3)
        cls.jan31 = datetime.date(2013, 1, 31)

    def test_accurate_definition(self):
        """Tests all ways of defining a FuzzyDate."""
        fuzz = fuzzy.FuzzyDate(self.jan1, self.jan31)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan31)

    def test_partial_definition(self):
        """Test defining a FuzzyDate without passing an end date."""
        with utils.mocked_date_today(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyDate(self.jan1)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan3)

    def test_invalid_definition(self):
        with self.assertRaises(ValueError):
            fuzzy.FuzzyDate(self.jan31, self.jan1)

    def test_invalid_partial_definition(self):
        with utils.mocked_date_today(self.jan1, fuzzy):
            with self.assertRaises(ValueError):
                fuzzy.FuzzyDate(self.jan31)

    def test_biased(self):
        """Tests a FuzzyDate with a biased random.randint."""

        fake_randint = lambda low, high: (low + high) // 2
        fuzz = fuzzy.FuzzyDate(self.jan1, self.jan31)

        with mock.patch('factory.random.randgen.randint', fake_randint):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(datetime.date(2013, 1, 16), res)

    def test_biased_partial(self):
        """Tests a FuzzyDate with a biased random and implicit upper bound."""
        with utils.mocked_date_today(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyDate(self.jan1)

        fake_randint = lambda low, high: (low + high) // 2
        with mock.patch('factory.random.randgen.randint', fake_randint):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(datetime.date(2013, 1, 2), res)


class FuzzyNaiveDateTimeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup useful constants
        cls.jan1 = datetime.datetime(2013, 1, 1)
        cls.jan3 = datetime.datetime(2013, 1, 3)
        cls.jan31 = datetime.datetime(2013, 1, 31)

    def test_accurate_definition(self):
        """Tests explicit definition of a FuzzyNaiveDateTime."""
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan31)

    def test_partial_definition(self):
        """Test defining a FuzzyNaiveDateTime without passing an end date."""
        with utils.mocked_datetime_now(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan3)

    def test_aware_start(self):
        """Tests that a timezone-aware start datetime is rejected."""
        with self.assertRaises(ValueError):
            fuzzy.FuzzyNaiveDateTime(self.jan1.replace(tzinfo=datetime.timezone.utc), self.jan31)

    def test_aware_end(self):
        """Tests that a timezone-aware end datetime is rejected."""
        with self.assertRaises(ValueError):
            fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31.replace(tzinfo=datetime.timezone.utc))

    def test_force_year(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_year=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.year)

    def test_force_month(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_month=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.month)

    def test_force_day(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_day=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.day)

    def test_force_hour(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_hour=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.hour)

    def test_force_minute(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_minute=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.minute)

    def test_force_second(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_second=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.second)

    def test_force_microsecond(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_microsecond=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.microsecond)

    def test_invalid_definition(self):
        with self.assertRaises(ValueError):
            fuzzy.FuzzyNaiveDateTime(self.jan31, self.jan1)

    def test_invalid_partial_definition(self):
        with utils.mocked_datetime_now(self.jan1, fuzzy):
            with self.assertRaises(ValueError):
                fuzzy.FuzzyNaiveDateTime(self.jan31)

    def test_biased(self):
        """Tests a FuzzyDate with a biased random.randint."""

        fake_randint = lambda low, high: (low + high) // 2
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31)

        with mock.patch('factory.random.randgen.randint', fake_randint):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(datetime.datetime(2013, 1, 16), res)

    def test_biased_partial(self):
        """Tests a FuzzyDate with a biased random and implicit upper bound."""
        with utils.mocked_datetime_now(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1)

        fake_randint = lambda low, high: (low + high) // 2
        with mock.patch('factory.random.randgen.randint', fake_randint):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(datetime.datetime(2013, 1, 2), res)


class FuzzyDateTimeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup useful constants
        cls.jan1 = datetime.datetime(2013, 1, 1, tzinfo=datetime.timezone.utc)
        cls.jan3 = datetime.datetime(2013, 1, 3, tzinfo=datetime.timezone.utc)
        cls.jan31 = datetime.datetime(2013, 1, 31, tzinfo=datetime.timezone.utc)

    def test_accurate_definition(self):
        """Tests explicit definition of a FuzzyDateTime."""
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan31)

    def test_partial_definition(self):
        """Test defining a FuzzyDateTime without passing an end date."""
        with utils.mocked_datetime_now(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyDateTime(self.jan1)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan3)

    def test_invalid_definition(self):
        with self.assertRaises(ValueError):
            fuzzy.FuzzyDateTime(self.jan31, self.jan1)

    def test_invalid_partial_definition(self):
        with utils.mocked_datetime_now(self.jan1, fuzzy):
            with self.assertRaises(ValueError):
                fuzzy.FuzzyDateTime(self.jan31)

    def test_naive_start(self):
        """Tests that a timezone-naive start datetime is rejected."""
        with self.assertRaises(ValueError):
            fuzzy.FuzzyDateTime(self.jan1.replace(tzinfo=None), self.jan31)

    def test_naive_end(self):
        """Tests that a timezone-naive end datetime is rejected."""
        with self.assertRaises(ValueError):
            fuzzy.FuzzyDateTime(self.jan1, self.jan31.replace(tzinfo=None))

    def test_force_year(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_year=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.year)

    def test_force_month(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_month=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.month)

    def test_force_day(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_day=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.day)

    def test_force_hour(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_hour=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.hour)

    def test_force_minute(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_minute=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.minute)

    def test_force_second(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_second=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.second)

    def test_force_microsecond(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_microsecond=4)

        for _i in range(20):
            res = utils.evaluate_declaration(fuzz)
            self.assertEqual(4, res.microsecond)

    def test_biased(self):
        """Tests a FuzzyDate with a biased random.randint."""

        fake_randint = lambda low, high: (low + high) // 2
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31)

        with mock.patch('factory.random.randgen.randint', fake_randint):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(datetime.datetime(2013, 1, 16, tzinfo=datetime.timezone.utc), res)

    def test_biased_partial(self):
        """Tests a FuzzyDate with a biased random and implicit upper bound."""
        with utils.mocked_datetime_now(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyDateTime(self.jan1)

        fake_randint = lambda low, high: (low + high) // 2
        with mock.patch('factory.random.randgen.randint', fake_randint):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual(datetime.datetime(2013, 1, 2, tzinfo=datetime.timezone.utc), res)


class FuzzyTextTestCase(unittest.TestCase):

    def test_unbiased(self):
        chars = ['a', 'b', 'c']
        fuzz = fuzzy.FuzzyText(prefix='pre', suffix='post', chars=chars, length=12)
        res = utils.evaluate_declaration(fuzz)

        self.assertEqual('pre', res[:3])
        self.assertEqual('post', res[-4:])
        self.assertEqual(3 + 12 + 4, len(res))

        for char in res[3:-4]:
            self.assertIn(char, chars)

    def test_mock(self):
        fake_choice = lambda chars: chars[0]

        chars = ['a', 'b', 'c']
        fuzz = fuzzy.FuzzyText(prefix='pre', suffix='post', chars=chars, length=4)
        with mock.patch('factory.random.randgen.choice', fake_choice):
            res = utils.evaluate_declaration(fuzz)

        self.assertEqual('preaaaapost', res)

    def test_generator(self):
        def options():
            yield 'a'
            yield 'b'
            yield 'c'

        fuzz = fuzzy.FuzzyText(chars=options(), length=12)
        res = utils.evaluate_declaration(fuzz)

        self.assertEqual(12, len(res))

        for char in res:
            self.assertIn(char, ['a', 'b', 'c'])


class FuzzyRandomTestCase(unittest.TestCase):
    def test_seeding(self):
        fuzz = fuzzy.FuzzyInteger(1, 1000)

        random.reseed_random(42)
        value = utils.evaluate_declaration(fuzz)

        random.reseed_random(42)
        value2 = utils.evaluate_declaration(fuzz)
        self.assertEqual(value, value2)

    def test_seeding_warning(self):
        with warnings.catch_warnings(record=True) as w:
            # Do not turn expected warning into an error.
            warnings.filterwarnings("default", category=UserWarning, module=r"tests\.test_fuzzy")
            fuzz = fuzzy.FuzzyDate(datetime.date(2013, 1, 1))
            utils.evaluate_declaration(fuzz)
            self.assertEqual(1, len(w))
            self.assertIn('factory_boy/issues/331', str(w[-1].message))

    def test_reset_state(self):
        fuzz = fuzzy.FuzzyInteger(1, 1000)

        state = random.get_random_state()
        value = utils.evaluate_declaration(fuzz)

        random.set_random_state(state)
        value2 = utils.evaluate_declaration(fuzz)
        self.assertEqual(value, value2)
