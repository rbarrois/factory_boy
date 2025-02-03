ChangeLog
=========

.. Note for v4.x: don't forget to check "Deprecated" sections for removal.

3.3.4 (unreleased)
------------------

- Nothing changed yet.


3.3.3 (2025-02-03)
------------------

*New:*

  - Publish type annotations


3.3.2 (2025-02-03)
------------------

*Bugfix:*

  - Fix docs generation

*New:*

  - Add support for Python 3.13


3.3.1 (2024-08-18)
------------------
*New:*

- Add support for Django 4.2
- Add support for Django 5.1
- Add support for Python 3.12
- :issue:`903`: Add basic typing annotations
- Run the test suite against ``mongomock`` instead of an actual MongoDB server

*Bugfix:*

- :issue:`1031`: Do not require :attr:`~factory.alchemy.SQLAlchemyOptions.sqlalchemy_session` when
  :attr:`~factory.alchemy.SQLAlchemyOptions.sqlalchemy_session_factory` is provided.
- :issue:`1072`: Allow using functions as models for a :attr:`~factory.FactoryOptions.model`.

*Removed:*

- Stop advertising and verifying support for Django 3.2, 4.0, 4.1

3.3.0 (2023-07-19)
------------------

*New:*

    - :issue:`366`: Add :class:`factory.django.Password` to generate Django :class:`~django.contrib.auth.models.User`
      passwords.
    - :issue:`304`: Add :attr:`~factory.alchemy.SQLAlchemyOptions.sqlalchemy_session_factory` to dynamically
      create sessions for use by the :class:`~factory.alchemy.SQLAlchemyModelFactory`.
    - Add support for Django 4.0
    - Add support for Django 4.1
    - Add support for Python 3.10
    - Add support for Python 3.11

*Bugfix:*

    - Make :meth:`~factory.django.mute_signals` mute signals during post-generation.

    - :issue:`775`: Change the signature for :class:`~factory.alchemy.SQLAlchemyModelFactory`'s ``_save`` and
      ``_get_or_create`` methods to avoid argument names clashes with a field named ``session``.

*Deprecated:*

    - :class:`~factory.django.DjangoModelFactory` will stop issuing a second call to
      :meth:`~django.db.models.Model.save` on the created instance when :ref:`post-generation-hooks` return a value.

      To help with the transition, :class:`factory.django.DjangoModelFactory`'s ``_after_postgeneration`` raises a
      :class:`DeprecationWarning` when calling :meth:`~django.db.models.Model.save`. Inspect your
      :class:`~factory.django.DjangoModelFactory` subclasses:

      - If the :meth:`~django.db.models.Model.save` call is not needed after :class:`~factory.PostGeneration`, set
        :attr:`factory.django.DjangoOptions.skip_postgeneration_save` to ``True`` in the factory meta.

      - Otherwise, the instance has been modified by :class:`~factory.PostGeneration` hooks and needs to be
        :meth:`~django.db.models.Model.save`\ d. Either:

          - call :meth:`django.db.models.Model.save` in the :class:`~factory.PostGeneration` hook that modifies the
            instance, or
          - override the :class:`~factory.Factory._after_postgeneration` method to
            :meth:`~django.db.models.Model.save` the instance.

*Removed:*

    - Drop support for Django 2.2
    - Drop support for Django 3.0
    - Drop support for Django 3.1
    - Drop support for Python 3.6
    - Drop support for Python 3.7

3.2.1 (2021-10-26)
------------------

*New:*
    - Add support for Django 3.2

*Bugfix:*

    - Do not override signals receivers registered in a :meth:`~factory.django.mute_signals` context.

    - :issue:`775`: Change the signature for :class:`~factory.alchemy.SQLAlchemyModelFactory`'s ``_save`` and
      ``_get_or_create`` methods to avoid argument names clashes with a field named ``session``.

3.2.0 (2020-12-28)
------------------

*New:*

    - Add support for Django 3.1
    - Add support for Python 3.9

*Removed:*

    - Drop support for Django 1.11. This version `is not maintained anymore <https://www.djangoproject.com/download/#supported-versions>`__.
    - Drop support for Python 3.5. This version `is not maintained anymore <https://devguide.python.org/developer-workflow/development-cycle/index.html#end-of-life-branches>`__.

*Deprecated:*

    - :func:`factory.use_strategy`. Use :attr:`factory.FactoryOptions.strategy` instead.
      The purpose of :func:`~factory.use_strategy` duplicates the factory option. Follow :pep:`20`: *There should be
      one-- and preferably only one --obvious way to do it.*

      :func:`~factory.use_strategy()` will be removed in the next major version.

*Bug fix:*

    - :issue:`785` :issue:`786` :issue:`787` :issue:`788` :issue:`790` :issue:`796`: Calls to :class:`factory.Faker`
      and :class:`factory.django.FileField` within a :class:`~factory.Trait` or :class:`~factory.Maybe` no longer lead to
      a ``KeyError`` crash.


3.1.0 (2020-10-02)
------------------

*New:*

    - Allow all types of declarations in :class:`factory.Faker` calls - enables references to other faker-defined attributes.


3.0.1 (2020-08-13)
------------------

*Bug fix:*

    - :issue:`769`: Fix ``import factory; factory.django.DjangoModelFactory`` and similar calls.


3.0.0 (2020-08-12)
------------------

Breaking changes
""""""""""""""""

The following aliases were removed:

+================================================+===================================================+
| Broken alias                                   | New import                                        |
+================================================+===================================================+
| ``from factory import DjangoModelFactory``     | ``from factory.django import DjangoModelFactory`` |
+------------------------------------------------+---------------------------------------------------+
| ``from factory import MogoFactory``            | ``from factory.mogo import MogoFactory``          |
+------------------------------------------------+---------------------------------------------------+
| ``from factory.fuzzy import get_random_state`` | ``from factory.random import get_random_state``   |
+------------------------------------------------+---------------------------------------------------+
| ``from factory.fuzzy import set_random_state`` | ``from factory.random import set_random_state``   |
+------------------------------------------------+---------------------------------------------------+
| ``from factory.fuzzy import reseed_random``    | ``from factory.random import reseed_random``      |
+================================================+===================================================+

*Removed:*

    - Drop support for Python 2 and 3.4. These versions `are not maintained anymore <https://devguide.python.org/developer-workflow/development-cycle/index.html#end-of-life-branches>`__.
    - Drop support for Django 2.0 and 2.1. These versions `are not maintained anymore <https://www.djangoproject.com/download/#supported-versions>`__.
    - Remove deprecated ``force_flush`` from ``SQLAlchemyModelFactory`` options. Use
      ``sqlalchemy_session_persistence = "flush"`` instead.
    - Drop deprecated ``attributes()`` from :class:`~factory.Factory` subclasses; use
      ``factory.make_factory(dict, FactoryClass._meta.pre_declarations)`` instead.
    - Drop deprecated ``declarations()`` from :class:`~factory.Factory` subclasses; use ``FactoryClass._meta.pre_declarations`` instead.
    - Drop ``factory.compat`` module.

*New:*

    - Add support for Python 3.8
    - Add support for Django 2.2 and 3.0
    - Report misconfiguration when a :py:class:`~factory.Factory` is used as the :py:attr:`~factory.FactoryOptions.model` for another :py:class:`~factory.Factory`.
    - Allow configuring the color palette of :py:class:`~factory.django.ImageField`.
    - :py:meth:`~factory.random.get_random_state()` now represents the state of Faker and ``factory_boy`` fuzzy attributes.
    - Add SQLAlchemy ``get_or_create`` support

*Improvements:*

    - :issue:`561`: Display a developer-friendly error message when providing a model instead of a factory in a :class:`~factory.SubFactory` class.

*Bug fix:*

    - Fix issue with SubFactory not preserving signal muting behavior of the used factory, thanks `Patrick Stein <https://github.com/PFStein>`_.
    - Fix issue with overriding parameters in a Trait, thanks `Grégoire Rocher <https://github.com/cecedille1>`_.
    - :issue:`598`: Limit ``get_or_create`` behavior to fields specified in ``django_get_or_create``.
    - :issue:`606`: Re-raise :class:`~django.db.IntegrityError` when ``django_get_or_create`` with multiple fields fails to lookup model using user provided keyword arguments.
    - :issue:`630`: TypeError masked by __repr__ AttributeError when initializing ``Maybe`` with inconsistent phases.


2.12.0 (2019-05-11)
-------------------

*New:*

    - Add support for Python 3.7
    - Add support for Django 2.1
    - Add ``getter`` to :class:`~factory.fuzzy.FuzzyChoice` that mimics
      the behavior of ``getter`` in :class:`~factory.Iterator`
    - Make the ``extra_kwargs`` parameter of :class:`~factory.Faker`'s ``generate`` method optional
    - Add :class:`~factory.RelatedFactoryList` class for one-to-many support, thanks `Sean Harrington <https://github.com/seanharr11>`_.
    - Make the `locale` argument for :class:`~factory.Faker` keyword-only

*Bug fix:*

    - Allow renamed arguments to be optional, thanks to `Justin Crown <https://github.com/mrname>`_.
    - Fix `django_get_or_create` behavior when using multiple fields with `unique=True`, thanks to `@YPCrumble <https://github.com/YPCrumble>`


2.11.1 (2018-05-05)
-------------------

*Bug fix:*

    - Fix passing deep context to a :class:`~factory.SubFactory` (``Foo(x__y__z=factory.Faker('name')``)


2.11.0 (2018-05-05)
-------------------

*Bug fix:*

    - Fix :class:`~factory.fuzzy.FuzzyFloat` to return a 15 decimal digits precision float by default
    - :issue:`451`: Restore :class:`~factory.django.FileField` to a
      ``factory.declarations.ParameteredAttribute``, relying on composition to parse the provided parameters.
    - :issue:`389`: Fix random state management with ``faker``.
    - :issue:`466`: Restore mixing :class:`~factory.Trait` and :meth:`~factory.post_generation`.


2.10.0 (2018-01-28)
-------------------

*Bug fix:*

    - :issue:`443`: Don't crash when calling :meth:`factory.Iterator.reset()` on a brand new iterator.

*New:*

    - :issue:`397`: Allow a :class:`factory.Maybe` to contain a :class:`~factory.PostGeneration` declaration.
      This also applies to :class:`factory.Trait`, since they use a :class:`factory.Maybe` declaration internally.

.. _v2.9.2:

2.9.2 (2017-08-03)
------------------

*Bug fix:*

    - Fix declaration corruption bug when a factory defined `foo__bar__baz=1` and a caller
      provided a `foo__bar=x` parameter at call time: this got merged into the factory's base
      declarations.

.. _v2.9.1:

2.9.1 (2017-08-02)
------------------

*Bug fix:*

    - Fix packaging issues (see https://github.com/zestsoftware/zest.releaser/issues/212)
    - Don't crash when debugging PostGenerationDeclaration

.. _v2.9.0:

2.9.0 (2017-07-30)
------------------

This version brings massive changes to the core engine, thus reducing the number of
corner cases and weird behaviors.

*New:*

    - :issue:`275`: `factory.fuzzy` and `factory.faker` now use the same random seed.
    - Add :class:`factory.Maybe`, which chooses among two possible declarations based
      on another field's value (powers the :class:`~factory.Trait` feature).
    - :class:`~factory.PostGenerationMethodCall` only allows to pass one positional argument; use keyword arguments for
      extra parameters.

*Deprecation:*

    - `factory.fuzzy.get_random_state` is deprecated, `factory.random.get_random_state` should be used instead.
    - `factory.fuzzy.set_random_state` is deprecated, `factory.random.set_random_state` should be used instead.
    - `factory.fuzzy.reseed_random` is deprecated, `factory.random.reseed_random` should be used instead.

.. _v2.8.1:

2.8.1 (2016-12-17)
------------------

*Bug fix:*

    - Fix packaging issues.


.. _v2.8.0:

2.8.0 (2016-12-17)
------------------

*New:*

    - :issue:`240`: Call post-generation declarations in the order they were declared,
      thanks to `Oleg Pidsadnyi <https://github.com/olegpidsadnyi>`_.
    - :issue:`309`: Provide new options for SQLAlchemy session persistence

*Bug fix:*

    - :issue:`334`: Adjust for the package change in ``faker``


.. _v2.7.0:

2.7.0 (2016-04-19)
------------------

*New:*

    - :pr:`267`: Add :class:`factory.LazyFunction` to remove unneeded lambda parameters,
      thanks to `Hervé Cauwelier <https://github.com/bors-ltd>`_.
    - :issue:`251`: Add :ref:`parameterized factories <parameters>` and :class:`traits <factory.Trait>`
    - :pr:`256`, :pr:`292`: Improve error messages in corner cases

*Removed:*

	- :pr:`278`: Formally drop support for Python2.6

.. warning:: Version 2.7.0 moves all error classes to
             `factory.errors`. This breaks existing import statements
             for any error classes except those importing
             `FactoryError` directly from the `factory` module.

.. _v2.6.1:

2.6.1 (2016-02-10)
------------------

*New:*

    - :pr:`262`: Allow optional forced flush on SQLAlchemy, courtesy of `Minjung <https://github.com/Minjung>`_.

.. _v2.6.0:

2.6.0 (2015-10-20)
------------------

*New:*

    - Add :attr:`factory.FactoryOptions.rename` to help handle conflicting names (:issue:`206`)
    - Add support for random-yet-realistic values through `fake-factory <https://pypi.org/project/fake-factory/>`_,
      through the :class:`factory.Faker` class.
    - :class:`factory.Iterator` no longer begins iteration of its argument at import time,
      thus allowing to pass in a lazy iterator such as a Django queryset
      (i.e ``factory.Iterator(models.MyThingy.objects.all())``).
    - Simplify imports for ORM layers, now available through a simple ``factory`` import,
      at ``factory.alchemy.SQLAlchemyModelFactory`` / ``factory.django.DjangoModelFactory`` / ``factory.mongoengine.MongoEngineFactory``.

*Bug fix:*

    - :issue:`201`: Properly handle custom Django managers when dealing with abstract Django models.
    - :issue:`212`: Fix :meth:`factory.django.mute_signals` to handle Django's signal caching
    - :issue:`228`: Don't load ``django.apps.apps.get_model()`` until required
    - :pr:`219`: Stop using ``mogo.model.Model.new()``, deprecated 4 years ago.

.. _v2.5.2:

2.5.2 (2015-04-21)
------------------

*Bug fix:*

    - Add support for Django 1.7/1.8
    - Add support for mongoengine>=0.9.0 / pymongo>=2.1

.. _v2.5.1:

2.5.1 (2015-03-27)
------------------

*Bug fix:*

    - Respect custom managers in :class:`~factory.django.DjangoModelFactory` (see :issue:`192`)
    - Allow passing declarations (e.g :class:`~factory.Sequence`) as parameters to :class:`~factory.django.FileField`
      and :class:`~factory.django.ImageField`.

.. _v2.5.0:

2.5.0 (2015-03-26)
------------------

*New:*

    - Add support for getting/setting :mod:`factory.fuzzy`'s random state (see :issue:`175`, :issue:`185`).
    - Support lazy evaluation of iterables in :class:`factory.fuzzy.FuzzyChoice` (see :issue:`184`).
    - Support non-default databases at the factory level (see :issue:`171`)
    - Make :class:`factory.django.FileField` and :class:`factory.django.ImageField` non-post_generation, i.e normal fields also available in ``save()`` (see :issue:`141`).

*Bug fix:*

    - Avoid issues when using :meth:`factory.django.mute_signals` on a base factory class (see :issue:`183`).
    - Fix limitations of :class:`factory.StubFactory`, that can now use :class:`factory.SubFactory` and co (see :issue:`131`).


*Deprecation:*

    - Remove deprecated features from :ref:`v2.4.0`
    - Remove the auto-magical sequence setup (based on the latest primary key value in the database) for Django and SQLAlchemy;
      this relates to issues :issue:`170`, :issue:`153`, :issue:`111`, :issue:`103`, :issue:`92`, :issue:`78`. See https://github.com/FactoryBoy/factory_boy/commit/13d310f for technical details.

.. warning:: Version 2.5.0 removes the 'auto-magical sequence setup' bug-and-feature.
             This could trigger some bugs when tests expected a non-zero sequence reference.

Upgrading
"""""""""

.. warning:: Version 2.5.0 removes features that were marked as deprecated in :ref:`v2.4.0 <v2.4.0>`.

All ``FACTORY_*``-style attributes are now declared in a ``class Meta:`` section:

.. code-block:: python

    # Old-style, deprecated
    class MyFactory(factory.Factory):
        FACTORY_FOR = models.MyModel
        FACTORY_HIDDEN_ARGS = ['a', 'b', 'c']

    # New-style
    class MyFactory(factory.Factory):
        class Meta:
            model = models.MyModel
            exclude = ['a', 'b', 'c']

A simple shell command to upgrade the code would be:

.. code-block:: sh

    # sed -i: inplace update
    # grep -l: only file names, not matching lines
    sed -i 's/FACTORY_FOR =/class Meta:\n        model =/' $(grep -l FACTORY_FOR $(find . -name '*.py'))

This takes care of all ``FACTORY_FOR`` occurrences; the files containing other attributes to rename can be found with ``grep -R  FACTORY .``


.. _v2.4.1:

2.4.1 (2014-06-23)
------------------

*Bug fix:*

    - Fix overriding deeply inherited attributes (set in one factory, overridden in a subclass, used in a sub-sub-class).

.. _v2.4.0:

2.4.0 (2014-06-21)
------------------

*New:*

    - Add support for :attr:`factory.fuzzy.FuzzyInteger.step`, thanks to `ilya-pirogov <https://github.com/ilya-pirogov>`_ (:pr:`120`)
    - Add :meth:`~factory.django.mute_signals` decorator to temporarily disable some signals, thanks to `ilya-pirogov <https://github.com/ilya-pirogov>`_ (:pr:`122`)
    - Add :class:`~factory.fuzzy.FuzzyFloat` (:issue:`124`)
    - Declare target model and other non-declaration fields in a ``class Meta`` section.

*Deprecation:*

    - Use of ``FACTORY_FOR`` and other ``FACTORY`` class-level attributes is deprecated and will be removed in 2.5.
      Those attributes should now declared within the :class:`class Meta <factory.FactoryOptions>` attribute:

      For :class:`factory.Factory`:

      * Rename ``factory.Factory.FACTORY_FOR`` to :attr:`~factory.FactoryOptions.model`
      * Rename ``factory.Factory.ABSTRACT_FACTORY`` to :attr:`~factory.FactoryOptions.abstract`
      * Rename ``factory.Factory.FACTORY_STRATEGY`` to :attr:`~factory.FactoryOptions.strategy`
      * Rename ``factory.Factory.FACTORY_ARG_PARAMETERS`` to :attr:`~factory.FactoryOptions.inline_args`
      * Rename ``factory.Factory.FACTORY_HIDDEN_ARGS`` to :attr:`~factory.FactoryOptions.exclude`

      For :class:`factory.django.DjangoModelFactory`:

      * Rename ``factory.django.DjangoModelFactory.FACTORY_DJANGO_GET_OR_CREATE`` to :attr:`~factory.django.DjangoOptions.django_get_or_create`

      For :class:`factory.alchemy.SQLAlchemyModelFactory`:

      * Rename ``factory.alchemy.SQLAlchemyModelFactory.FACTORY_SESSION`` to :attr:`~factory.alchemy.SQLAlchemyOptions.sqlalchemy_session`

.. _v2.3.1:

2.3.1 (2014-01-22)
------------------

*Bug fix:*

    - Fix badly written assert containing state-changing code, spotted by ``chsigi`` (:pr:`126`)
    - Don't crash when handling objects whose ``__repr__`` is non-pure-ASCII bytes on Python 2,
      discovered by `mbertheau <https://github.com/mbertheau>`_ (:issue:`123`) and `strycore <https://github.com/strycore>`_ (:pr:`127`)

.. _v2.3.0:

2.3.0 (2013-12-25)
------------------

*New:*

    - Add :class:`~factory.fuzzy.FuzzyText`, thanks to `jdufresne <https://github.com/jdufresne>`_ (:pr:`97`)
    - Add :class:`~factory.fuzzy.FuzzyDecimal`, thanks to `thedrow <https://github.com/thedrow>`_ (:pr:`94`)
    - Add support for :class:`~mongoengine.EmbeddedDocument`, thanks to `imiric <https://github.com/imiric>`_ (:pr:`100`)

.. _v2.2.1:

2.2.1 (2013-09-24)
------------------

*Bug fix:*

    - Fixed sequence counter for :class:`~factory.django.DjangoModelFactory` when a factory
      inherits from another factory relating to an abstract model.

.. _v2.2.0:

2.2.0 (2013-09-24)
------------------

*Bug fix:*

    - Removed duplicated :class:`~factory.alchemy.SQLAlchemyModelFactory` lurking in :mod:`factory`
      (:pr:`83`)
    - Properly handle sequences within object inheritance chains.
      If ``FactoryA`` inherits from ``FactoryB``, and their associated classes
      share the same link, sequence counters will be shared (:issue:`93`)
    - Properly handle nested :class:`~factory.SubFactory` overrides

*New:*

    - The :class:`~factory.django.DjangoModelFactory` now supports the ``FACTORY_FOR = 'myapp.MyModel'``
      syntax, making it easier to shove all factories in a single module (:issue:`66`).
    - Add :meth:`factory.debug()` helper for easier backtrace analysis
    - Adding factory support for mongoengine with :class:`~factory.mongoengine.MongoEngineFactory`.

.. _v2.1.2:

2.1.2 (2013-08-14)
------------------

*New:*

    - The ``factory.Factory.ABSTRACT_FACTORY`` keyword is now optional, and automatically set
      to ``True`` if neither the :class:`~factory.Factory` subclass nor its parent declare the
      ``factory.Factory.FACTORY_FOR`` attribute (:issue:`74`)


.. _v2.1.1:

2.1.1 (2013-07-02)
------------------

*Bug fix:*

    - Properly retrieve the ``color`` keyword argument passed to :class:`~factory.django.ImageField`

.. _v2.1.0:

2.1.0 (2013-06-26)
------------------

*New:*

    - Add :class:`~factory.fuzzy.FuzzyDate` thanks to `saulshanabrook <https://github.com/saulshanabrook>`_
    - Add :class:`~factory.fuzzy.FuzzyDateTime` and :class:`~factory.fuzzy.FuzzyNaiveDateTime`.
    - Add a ``factory_parent`` attribute to the
      ``factory.builder.Resolver`` passed to :class:`~factory.LazyAttribute`, in order to access
      fields defined in wrapping factories.
    - Move :class:`~factory.django.DjangoModelFactory` and :class:`~factory.mogo.MogoFactory`
      to their own modules (:mod:`factory.django` and :mod:`factory.mogo`)
    - Add the :meth:`~factory.Factory.reset_sequence` classmethod to :class:`~factory.Factory`
      to ease resetting the sequence counter for a given factory.
    - Add debug messages to ``factory`` logger.
    - Add a :meth:`~factory.Iterator.reset` method to :class:`~factory.Iterator` (:issue:`63`)
    - Add support for the SQLAlchemy ORM through :class:`~factory.alchemy.SQLAlchemyModelFactory`
      (:pr:`64`, thanks to `Romain Commandé <https://github.com/rcommande>`_)
    - Add :class:`factory.django.FileField` and :class:`factory.django.ImageField` hooks for
      related Django model fields (:issue:`52`)

*Bug fix*

    - Properly handle non-integer primary keys in :class:`~factory.django.DjangoModelFactory` (:issue:`57`).
    - Disable :class:`~factory.RelatedFactory` generation when a specific value was
      passed (:issue:`62`, thanks to `Gabe Koscky <https://github.com/dhekke>`_)

*Deprecation:*

    - Rename :class:`~factory.RelatedFactory`'s ``name`` argument to ``factory_related_name`` (See :issue:`58`)


.. _v2.0.2:

2.0.2 (2013-04-16)
------------------

*New:*

    - When ``factory.django.DjangoModelFactory.FACTORY_DJANGO_GET_OR_CREATE`` is
      empty, use ``Model.objects.create()`` instead of ``Model.objects.get_or_create``.


.. _v2.0.1:

2.0.1 (2013-04-16)
------------------

*New:*

    - Don't push ``defaults`` to ``get_or_create`` when
      ``factory.django.DjangoModelFactory.FACTORY_DJANGO_GET_OR_CREATE`` is not set.


.. _v2.0.0:

2.0.0 (2013-04-15)
------------------

*New:*

    - Allow overriding the base factory class for :func:`~factory.make_factory` and friends.
    - Add support for Python3 (Thanks to `kmike <https://github.com/kmike>`_ and `nkryptic <https://github.com/nkryptic>`_)
    - The default type for :class:`~factory.Sequence` is now :obj:`int`
    - Fields listed in ``factory.Factory.FACTORY_HIDDEN_ARGS`` won't be passed to
      the associated class' constructor
    - Add support for ``get_or_create`` in :class:`~factory.django.DjangoModelFactory`,
      through ``factory.django.DjangoModelFactory.FACTORY_DJANGO_GET_OR_CREATE``.
    - Add support for :mod:`~factory.fuzzy` attribute definitions.
    - The :class:`Sequence` counter can be overridden when calling a generating function
    - Add :class:`~factory.Dict` and :class:`~factory.List` declarations (Closes :issue:`18`).

*Removed:*

    - Remove associated class discovery
    - Remove ``factory.InfiniteIterator`` and ``factory.infinite_iterator``
    - Remove ``factory.CircularSubFactory``
    - Remove ``extract_prefix`` kwarg to post-generation hooks.
    - Stop defaulting to Django's ``Foo.objects.create()`` when "creating" instances
    - Remove STRATEGY_*
    - Remove ``factory.Factory.set_building_function`` / ``factory.Factory.set_creation_function``


.. _v1.3.0:

1.3.0 (2013-03-11)
------------------

.. warning:: This version deprecates many magic or unexplicit features that will be
             removed in v2.0.0.

             Please read the :ref:`changelog-1-3-0-upgrading` section, then run your
             tests with ``python -W default`` to see all remaining warnings.

New
"""

- **Global:**
    - Rewrite the whole documentation
    - Provide a dedicated :class:`~factory.mogo.MogoFactory` subclass of :class:`~factory.Factory`

- **The Factory class:**
    - Better creation/building customization hooks at :meth:`factory.Factory._build` and :meth:`factory.Factory.create`
    - Add support for passing non-kwarg parameters to a :class:`~factory.Factory`
      wrapped class through ``FACTORY_ARG_PARAMETERS``.
    - Keep the ``FACTORY_FOR`` attribute in :class:`~factory.Factory` classes

- **Declarations:**
    - Allow :class:`~factory.SubFactory` to solve circular dependencies between factories
    - Enhance :class:`~factory.SelfAttribute` to handle "container" attribute fetching
    - Add a :attr:`~factory.Iterator.getter` to :class:`~factory.Iterator`
      declarations
    - A :class:`~factory.Iterator` may be prevented from cycling by setting
      its :attr:`~factory.Iterator.cycle` argument to ``False``
    - Allow overriding default arguments in a :class:`~factory.PostGenerationMethodCall`
      when generating an instance of the factory
    - An object created by a :class:`~factory.django.DjangoModelFactory` will be saved
      again after :class:`~factory.PostGeneration` hooks execution


Pending deprecation
"""""""""""""""""""

The following features have been deprecated and will be removed in an upcoming release.

- **Declarations:**
    - ``factory.InfiniteIterator`` is deprecated in favor of :class:`~factory.Iterator`
    - ``factory.CircularSubFactory`` is deprecated in favor of :class:`~factory.SubFactory`
    - The ``extract_prefix`` argument to :meth:`~factory.post_generation` is now deprecated

- **Factory:**
    - Usage of ``factory.Factory.set_creation_function`` and ``factory.Factory.set_building_function``
      are now deprecated
    - Implicit associated class discovery is no longer supported, you must set the ``FACTORY_FOR``
      attribute on all :class:`~factory.Factory` subclasses


.. _changelog-1-3-0-upgrading:

Upgrading
"""""""""

This version deprecates a few magic or undocumented features.
All warnings will turn into errors starting from v2.0.0.

In order to upgrade client code, apply the following rules:

- Add a ``FACTORY_FOR`` attribute pointing to the target class to each
  :class:`~factory.Factory`, instead of relying on automatic associated class
  discovery
- When using factory_boy for Django models, have each factory inherit from
  :class:`~factory.django.DjangoModelFactory`
- Replace ``factory.CircularSubFactory('some.module', 'Symbol')`` with
  ``factory.SubFactory('some.module.Symbol')``
- Replace ``factory.InfiniteIterator(iterable)`` with ``factory.Iterator(iterable)``
- Replace ``@factory.post_generation()`` with ``@factory.post_generation``
- Replace ``factory.set_building_function(SomeFactory, building_function)`` with
  an override of the :meth:`~factory.Factory._build` method of ``SomeFactory``
- Replace ``factory.set_creation_function(SomeFactory, creation_function)`` with
  an override of the :meth:`~factory.Factory._create` method of ``SomeFactory``



.. _v1.2.0:

1.2.0 (2012-09-08)
------------------

*New:*

    - Add ``factory.CircularSubFactory`` to solve circular dependencies between factories


.. _v1.1.5:

1.1.5 (2012-07-09)
------------------

*Bug fix:*

    - Fix ``factory.PostGenerationDeclaration`` and derived classes.


.. _v1.1.4:

1.1.4 (2012-06-19)
------------------

*New:*

    - Add :meth:`~factory.use_strategy` decorator to override a
      :class:`~factory.Factory`'s default strategy
    - Improve test running (tox, python2.6/2.7)
    - Introduce :class:`~factory.PostGeneration` and
      :class:`~factory.RelatedFactory`


.. _v1.1.3:

1.1.3 (2012-03-09)
------------------

*Bug fix:*

  - Fix packaging rules


.. _v1.1.2:

1.1.2 (2012-02-25)
------------------

*New:*

  - Add :class:`~factory.Iterator` and ``factory.InfiniteIterator`` for :class:`~factory.Factory` attribute declarations.
  - Provide :func:`~factory.Factory.generate` and :func:`~factory.Factory.simple_generate`, that allow specifying the instantiation strategy directly.
    Also provides :func:`~factory.Factory.generate_batch` and :func:`~factory.Factory.simple_generate_batch`.


.. _v1.1.1:

1.1.1 (2012-02-24)
------------------

*New:*

  - Add :func:`~factory.Factory.build_batch`, :func:`~factory.Factory.create_batch` and :func:`~factory.Factory.stub_batch`, to instantiate factories in batch


.. _v1.1.0:

1.1.0 (2012-02-24)
------------------

*New:*

  - Improve the :class:`~factory.SelfAttribute` syntax to fetch sub-attributes using the ``foo.bar`` syntax;
  - Add ``factory.ContainerAttribute`` to fetch attributes from the container of a :class:`~factory.SubFactory`.
  - Provide the :func:`~factory.make_factory` helper: ``MyClassFactory = make_factory(MyClass, x=3, y=4)``
  - Add :func:`~factory.build`, :func:`~factory.create`, :func:`~factory.stub` helpers

*Bug fix:*

  - Allow ``classmethod``/``staticmethod`` on factories

*Deprecation:*

  - Auto-discovery of ``factory.Factory.FACTORY_FOR`` based on class name is now deprecated


.. _v1.0.4:

1.0.4 (2011-12-21)
------------------

*New:*

  - Improve the algorithm for populating a :class:`~factory.Factory` attributes dict
  - Add ``python setup.py test`` command to run the test suite
  - Allow custom build functions
  - Introduce ``factory.MOGO_BUILD`` build function
  - Add support for inheriting from multiple :class:`~factory.Factory`
  - Base :class:`~factory.Factory` classes can now be declared abstract through ``factory.Factory.ABSTRACT_FACTORY``.
  - Provide :class:`~factory.django.DjangoModelFactory`, whose :class:`~factory.Sequence` counter starts at the next free database id
  - Introduce :class:`~factory.SelfAttribute`, a shortcut for ``factory.LazyAttribute(lambda o: o.foo.bar.baz``.

*Bug fix:*

  - Handle nested :class:`~factory.SubFactory`
  - Share sequence counter between parent and subclasses
  - Fix :class:`~factory.SubFactory` / :class:`~factory.Sequence` interference


.. _v1.0.2:

1.0.2 (2011-05-16)
------------------

*New:*

  - Introduce :class:`~factory.SubFactory`


.. _v1.0.1:

1.0.1 (2011-05-13)
------------------

*New:*

  - Allow :class:`~factory.Factory` inheritance
  - Improve handling of custom build/create functions

*Bug fix:*

  - Fix concurrency between :class:`~factory.LazyAttribute` and :class:`~factory.Sequence`


.. _v1.0.0:

1.0.0 (2010-08-22)
------------------

*New:*

  - First version of factory_boy


Credits
-------

See :doc:`credits`.

.. vim:et:ts=4:sw=4:tw=119:ft=rst:
