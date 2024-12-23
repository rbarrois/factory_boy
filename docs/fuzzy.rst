Fuzzy attributes
================

.. module:: factory.fuzzy

.. note:: Now that FactoryBoy includes the :class:`factory.Faker` class, most of
          these built-in fuzzers are deprecated in favor of their
          `Faker <https://faker.readthedocs.io/>`_ equivalents. Further
          discussion in :issue:`271`.

Some tests may be interested in testing with fuzzy, random values.

This is handled by the :mod:`factory.fuzzy` module, which provides a few
random declarations.

.. note:: Use ``import factory.fuzzy`` to load this module.


FuzzyAttribute
--------------


.. class:: FuzzyAttribute

    The :class:`FuzzyAttribute` uses an arbitrary callable as fuzzer.
    It is expected that successive calls of that function return various
    values.

    .. attribute:: fuzzer

        The callable that generates random values


FuzzyText
---------


.. class:: FuzzyText(length=12, chars=string.ascii_letters, prefix='')

    The :class:`FuzzyText` fuzzer yields random strings beginning with
    the given :attr:`prefix`, followed by :attr:`length` characters chosen
    from the :attr:`chars` character set,
    and ending with the given :attr:`suffix`.

    .. attribute:: length

        int, the length of the random part

    .. attribute:: prefix

        text, an optional prefix to prepend to the random part

    .. attribute:: suffix

        text, an optional suffix to append to the random part

    .. attribute:: chars

        char iterable, the chars to choose from; defaults to the list of ascii
            letters and numbers.


FuzzyChoice
-----------


.. class:: FuzzyChoice(choices)

    The :class:`FuzzyChoice` fuzzer yields random choices from the given
    iterable.

    .. note:: The passed in :attr:`choices` will be converted into a list upon
              first use, not at declaration time.

              This allows passing in, for instance, a Django queryset that will
              only hit the database during the database, not at import time.

    .. attribute:: choices

        The list of choices to select randomly


FuzzyInteger
------------

.. class:: FuzzyInteger(low[, high[, step]])

    The :class:`FuzzyInteger` fuzzer generates random integers within a given
    inclusive range.

    The :attr:`low` bound may be omitted, in which case it defaults to 0:

    .. code-block:: pycon

        >>> fi = FuzzyInteger(0, 42)
        >>> fi.low, fi.high
        0, 42

        >>> fi = FuzzyInteger(42)
        >>> fi.low, fi.high
        0, 42

    .. attribute:: low

        int, the inclusive lower bound of generated integers

    .. attribute:: high

        int, the inclusive higher bound of generated integers

    .. attribute:: step

        int, the step between values in the range; for instance, a ``FuzzyInteger(0, 42, step=3)``
        might only yield values from ``[0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42]``.


FuzzyDecimal
------------

.. class:: FuzzyDecimal(low[, high[, precision=2]])

    The :class:`FuzzyDecimal` fuzzer generates random :class:`decimals <decimal.Decimal>` within a given
    inclusive range.

    .. note::
        Providing decimals as argument will result in a :exc:`TypeError`. Use :class:`~factory.fuzzy.FuzzyDecimalDec`
        instead.

    The :attr:`low` bound may be omitted, in which case it defaults to 0:

    .. code-block:: pycon

        >>> fd = FuzzyDecimal(0.5, 42.7)
        >>> fd.low, fd.high
        0.5, 42.7

        >>> fd = FuzzyDecimal(42.7)
        >>> fd.low, fd.high
        0.0, 42.7

        >>> fd = FuzzyDecimal(0.5, 42.7, 3)
        >>> fd.low, fd.high, fd.precision
        0.5, 42.7, 3

    .. attribute:: low

        float or int, the inclusive lower bound of generated decimals

    .. attribute:: high

        float or int, the inclusive higher bound of generated decimals

    .. attribute:: precision

        int, the number of digits after the decimal separator. The default is 2.


FuzzyDecimalDec
---------------

.. class:: FuzzyDecimalDec(low[, high[, precision=2]])

    The :class:`FuzzyDecimalDec` fuzzer generates random :class:`decimals <decimal.Decimal>` within a given
    inclusive range, accepting any argument that the constructor of the :class:`decimal <decimal.Decimal>`
    accepts.

    .. note::
        One purpose of this class is accuracy. Providing inaccurate arguments (:class:`floats <float>`), will result in
        inaccurate bounds. In that case it's better to use :class:`~factory.fuzzy.FuzzyDecimal` instead.

    The :attr:`low` bound may be omitted, in which case it defaults to 0:

    .. code-block:: pycon

        >>> fd = FuzzyDecimalDec('0.5', Decimal('42.7'))
        >>> fd.low, fd.high
        Decimal('0.5'), Decimal('42.7')

        >>> fd = FuzzyDecimalDec(42.7)
        >>> fd.low, fd.high
        Decimal('0'), Decimal('42.7000000000000028421709430404007434844970703125')

        >>> fd = FuzzyDecimalDec('0.5', '42.7', 3)
        >>> fd.low, fd.high, fd.precision
        Decimal('0.5'), Decimal('42.7'), 3

    .. attribute:: low

        string, Decimal or int, the inclusive lower bound of generated decimals

    .. attribute:: high

        string, Decimal or int, the inclusive higher bound of generated decimals

    .. attribute:: precision

        int, the number of digits after the decimal separator. The default is 2.


FuzzyFloat
----------

.. class:: FuzzyFloat(low[, high])

    The :class:`FuzzyFloat` fuzzer provides random :class:`float` objects within a given inclusive range.

    .. code-block:: pycon

        >>> FuzzyFloat(0.5, 42.7)
        >>> fi.low, fi.high
        0.5, 42.7

        >>> fi = FuzzyFloat(42.7)
        >>> fi.low, fi.high
        0.0, 42.7


    .. attribute:: low

        decimal, the inclusive lower bound of generated floats

    .. attribute:: high

        decimal, the inclusive higher bound of generated floats

FuzzyDate
---------

.. class:: FuzzyDate(start_date[, end_date])

    The :class:`FuzzyDate` fuzzer generates random dates within a given
    inclusive range.

    The :attr:`end_date` bound may be omitted, in which case it defaults to the current date:

    .. code-block:: pycon

        >>> fd = FuzzyDate(datetime.date(2008, 1, 1))
        >>> fd.start_date, fd.end_date
        datetime.date(2008, 1, 1), datetime.date(2013, 4, 16)

    .. attribute:: start_date

        :class:`datetime.date`, the inclusive lower bound of generated dates

    .. attribute:: end_date

        :class:`datetime.date`, the inclusive higher bound of generated dates


FuzzyDateTime
-------------

.. class:: FuzzyDateTime(start_dt[, end_dt], force_year=None, force_month=None, force_day=None, force_hour=None, force_minute=None, force_second=None, force_microsecond=None)

    The :class:`FuzzyDateTime` fuzzer generates random timezone-aware datetime within a given
    inclusive range.

    The :attr:`end_dt` bound may be omitted, in which case it defaults to ``datetime.datetime.now()``
    localized into the UTC timezone.

    .. code-block:: pycon

        >>> fdt = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC))
        >>> fdt.start_dt, fdt.end_dt
        datetime.datetime(2008, 1, 1, tzinfo=UTC), datetime.datetime(2013, 4, 21, 19, 13, 32, 458487, tzinfo=UTC)


    The ``force_XXX`` keyword arguments force the related value of generated datetimes:

    .. code-block:: pycon

        >>> fdt = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC), datetime.datetime(2009, 1, 1, tzinfo=UTC),
        ...     force_day=3, force_second=42)
        >>> fdt.evaluate(2, None, False)  # Actual code used by ``SomeFactory.build()``
        datetime.datetime(2008, 5, 3, 12, 13, 42, 124848, tzinfo=UTC)


    .. attribute:: start_dt

        :class:`datetime.datetime`, the inclusive lower bound of generated datetimes

    .. attribute:: end_dt

        :class:`datetime.datetime`, the inclusive upper bound of generated datetimes


    .. attribute:: force_year

        int or None; if set, forces the :attr:`~datetime.datetime.year` of generated datetime.

    .. attribute:: force_month

        int or None; if set, forces the :attr:`~datetime.datetime.month` of generated datetime.

    .. attribute:: force_day

        int or None; if set, forces the :attr:`~datetime.datetime.day` of generated datetime.

    .. attribute:: force_hour

        int or None; if set, forces the :attr:`~datetime.datetime.hour` of generated datetime.

    .. attribute:: force_minute

        int or None; if set, forces the :attr:`~datetime.datetime.minute` of generated datetime.

    .. attribute:: force_second

        int or None; if set, forces the :attr:`~datetime.datetime.second` of generated datetime.

    .. attribute:: force_microsecond

        int or None; if set, forces the :attr:`~datetime.datetime.microsecond` of generated datetime.


FuzzyNaiveDateTime
------------------

.. class:: FuzzyNaiveDateTime(start_dt[, end_dt], force_year=None, force_month=None, force_day=None, force_hour=None, force_minute=None, force_second=None, force_microsecond=None)

    The :class:`FuzzyNaiveDateTime` fuzzer generates random naive datetime within a given
    inclusive range.

    The :attr:`end_dt` bound may be omitted, in which case it defaults to ``datetime.datetime.now()``:

    .. code-block:: pycon

        >>> fdt = FuzzyNaiveDateTime(datetime.datetime(2008, 1, 1))
        >>> fdt.start_dt, fdt.end_dt
        datetime.datetime(2008, 1, 1), datetime.datetime(2013, 4, 21, 19, 13, 32, 458487)


    The ``force_XXX`` keyword arguments force the related value of generated datetimes:

    .. code-block:: pycon

        >>> fdt = FuzzyNaiveDateTime(datetime.datetime(2008, 1, 1), datetime.datetime(2009, 1, 1),
        ...     force_day=3, force_second=42)
        >>> fdt.evaluate(2, None, False)  # Actual code used by ``SomeFactory.build()``
        datetime.datetime(2008, 5, 3, 12, 13, 42, 124848)


    .. attribute:: start_dt

        :class:`datetime.datetime`, the inclusive lower bound of generated datetimes

    .. attribute:: end_dt

        :class:`datetime.datetime`, the inclusive upper bound of generated datetimes


    .. attribute:: force_year

        int or None; if set, forces the :attr:`~datetime.datetime.year` of generated datetime.

    .. attribute:: force_month

        int or None; if set, forces the :attr:`~datetime.datetime.month` of generated datetime.

    .. attribute:: force_day

        int or None; if set, forces the :attr:`~datetime.datetime.day` of generated datetime.

    .. attribute:: force_hour

        int or None; if set, forces the :attr:`~datetime.datetime.hour` of generated datetime.

    .. attribute:: force_minute

        int or None; if set, forces the :attr:`~datetime.datetime.minute` of generated datetime.

    .. attribute:: force_second

        int or None; if set, forces the :attr:`~datetime.datetime.second` of generated datetime.

    .. attribute:: force_microsecond

        int or None; if set, forces the :attr:`~datetime.datetime.microsecond` of generated datetime.


Custom fuzzy fields
-------------------

Alternate fuzzy fields may be defined.
They should inherit from the :class:`BaseFuzzyAttribute` class, and override its
:meth:`~BaseFuzzyAttribute.fuzz` method.


.. class:: BaseFuzzyAttribute

    Base class for all fuzzy attributes.

    .. method:: fuzz(self)

        The method responsible for generating random values.
        *Must* be overridden in subclasses.

    .. warning::

        Custom :class:`BaseFuzzyAttribute` subclasses **MUST**
        use :obj:`factory.random.randgen` as a randomness source; this ensures that
        data they generate can be regenerated using the simple state from
        :meth:`factory.random.get_random_state`.
