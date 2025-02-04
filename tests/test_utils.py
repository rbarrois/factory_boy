# Copyright: See the LICENSE file.

import datetime
import itertools
import unittest

from factory import utils


class ImportObjectTestCase(unittest.TestCase):
    def test_datetime(self):
        imported = utils.import_object('datetime', 'date')
        self.assertEqual(datetime.date, imported)

    def test_unknown_attribute(self):
        with self.assertRaises(AttributeError):
            utils.import_object('datetime', 'foo')

    def test_invalid_module(self):
        with self.assertRaises(ImportError):
            utils.import_object('this-is-an-invalid-module', '__name__')


class ResolveTypeTestCase(unittest.TestCase):
    def test_datetime(self):
        imported = utils.resolve_type('datetime.date')
        self.assertEqual(datetime.date, imported)

    def test_unknown_attribute(self):
        with self.assertRaises(AttributeError):
            utils.resolve_type('datetime.foo')

    def test_invalid_module(self):
        with self.assertRaises(ImportError):
            utils.resolve_type('this-is-an-invalid-module.__name__')

    def test_is_a_class(self):
        return utils.resolve_type(datetime.date) is datetime.date


class LogPPrintTestCase(unittest.TestCase):
    def test_nothing(self):
        txt = str(utils.log_pprint())
        self.assertEqual('', txt)

    def test_only_args(self):
        txt = str(utils.log_pprint((1, 2, 3)))
        self.assertEqual('1, 2, 3', txt)

    def test_only_kwargs(self):
        txt = str(utils.log_pprint(kwargs={'a': 1, 'b': 2}))
        self.assertIn(txt, ['a=1, b=2', 'b=2, a=1'])

    def test_bytes_args(self):
        txt = str(utils.log_pprint((b'\xe1\xe2',)))
        expected = "b'\\xe1\\xe2'"
        self.assertEqual(expected, txt)

    def test_text_args(self):
        txt = str(utils.log_pprint(('ŧêßŧ',)))
        expected = "'ŧêßŧ'"
        self.assertEqual(expected, txt)

    def test_bytes_kwargs(self):
        txt = str(utils.log_pprint(kwargs={'x': b'\xe1\xe2', 'y': b'\xe2\xe1'}))
        expected1 = "x=b'\\xe1\\xe2', y=b'\\xe2\\xe1'"
        expected2 = "y=b'\\xe2\\xe1', x=b'\\xe1\\xe2'"
        self.assertIn(txt, (expected1, expected2))

    def test_text_kwargs(self):
        txt = str(utils.log_pprint(kwargs={'x': 'ŧêßŧ', 'y': 'ŧßêŧ'}))
        expected1 = "x='ŧêßŧ', y='ŧßêŧ'"
        expected2 = "y='ŧßêŧ', x='ŧêßŧ'"
        self.assertIn(txt, (expected1, expected2))


class ResetableIteratorTestCase(unittest.TestCase):
    def test_no_reset(self):
        i = utils.ResetableIterator([1, 2, 3])
        self.assertEqual([1, 2, 3], list(i))

    def test_no_reset_new_iterator(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))

        iterator2 = iter(i)
        self.assertEqual(3, next(iterator2))

    def test_infinite(self):
        i = utils.ResetableIterator(itertools.cycle([1, 2, 3]))
        iterator = iter(i)
        values = [next(iterator) for _i in range(10)]
        self.assertEqual([1, 2, 3, 1, 2, 3, 1, 2, 3, 1], values)

    def test_reset_simple(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

    def test_reset_at_begin(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        i.reset()
        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

    def test_reset_at_end(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

    def test_reset_after_end(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        with self.assertRaises(StopIteration):
            next(iterator)

        i.reset()
        # Previous iter() has stopped
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

    def test_reset_twice(self):
        i = utils.ResetableIterator([1, 2, 3, 4, 5])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertEqual(4, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertEqual(4, next(iterator))

    def test_reset_shorter(self):
        i = utils.ResetableIterator([1, 2, 3, 4, 5])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertEqual(4, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertEqual(4, next(iterator))
