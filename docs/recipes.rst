Common recipes
==============


.. note:: Most recipes below take on Django model examples, but can also be used on their own.


Dependent objects (ForeignKey)
------------------------------

When one attribute is actually a complex field
(e.g a :class:`~django.db.models.ForeignKey` to another :class:`~django.db.models.Model`),
use the :class:`~factory.SubFactory` declaration:


.. code-block:: python

    # models.py
    class User(models.Model):
        first_name = models.CharField()
        group = models.ForeignKey(Group)


    # factories.py
    import factory
    from . import models

    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.User

        first_name = factory.Sequence(lambda n: "Agent %03d" % n)
        group = factory.SubFactory(GroupFactory)


Choosing from a populated table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the target of the :class:`~django.db.models.ForeignKey` should be
chosen from a pre-populated table
(e.g :class:`django.contrib.contenttypes.models.ContentType`),
simply use a :class:`factory.Iterator` on the chosen queryset:

.. code-block:: python

    import factory, factory.django
    from . import models

    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.User

        language = factory.Iterator(models.Language.objects.all())

Here, ``models.Language.objects.all()`` is a
:class:`~django.db.models.query.QuerySet` and will only hit the database when
``factory_boy`` starts iterating on it, i.e on the first call to
``UserFactory``; thus avoiding DB queries at import time.


Reverse dependencies (reverse ForeignKey)
-----------------------------------------

When a related object should be created upon object creation
(e.g a reverse :class:`~django.db.models.ForeignKey` from another :class:`~django.db.models.Model`),
use a :class:`~factory.RelatedFactory` declaration:


.. code-block:: python

    # models.py
    class User(models.Model):
        pass

    class UserLog(models.Model):
        user = models.ForeignKey(User)
        action = models.CharField()


    # factories.py
    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.User

        log = factory.RelatedFactory(
            UserLogFactory,
            factory_related_name='user',
            action=models.UserLog.ACTION_CREATE,
        )


When a ``UserFactory`` is instantiated, factory_boy will call
``UserLogFactory(user=that_user, action=...)`` just before returning the created ``User``.


Example: Django's Profile
~~~~~~~~~~~~~~~~~~~~~~~~~

Django (<1.5) provided a mechanism to attach a ``Profile`` to a ``User`` instance,
using a :class:`~django.db.models.OneToOneField` from the ``Profile`` to the ``User``.

A typical way to create those profiles was to hook a post-save signal to the ``User`` model.

Prior to version 2.9, the solution to this was to override the ``factory.Factory._generate`` method on the factory.

Since version 2.9, the :meth:`~factory.django.mute_signals` decorator should be used:


.. code-block:: python

    from django.db.models.signals import post_save
    
    @factory.django.mute_signals(post_save)
    class ProfileFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = my_models.Profile

        title = 'Dr'
        # We pass in profile=None to prevent UserFactory from creating another profile
        # (this disables the RelatedFactory)
        user = factory.SubFactory('app.factories.UserFactory', profile=None)

    @factory.django.mute_signals(post_save)
    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = auth_models.User

        username = factory.Sequence(lambda n: "user_%d" % n)

        # We pass in 'user' to link the generated Profile to our just-generated User
        # This will call ProfileFactory(user=our_new_user), thus skipping the SubFactory.
        profile = factory.RelatedFactory(ProfileFactory, factory_related_name='user')

.. OHAI_VIM:*


.. code-block:: pycon

    >>> u = UserFactory(profile__title="Lord")
    >>> u.get_profile().title
    "Lord"

Such behavior can be extended to other situations where a signal interferes with
factory_boy related factories.

Any factories that call these classes with :class:`~factory.SubFactory` will also need to be decorated in the same manner.

..
   _DEPRECATED: Release 4.0: post_generation and RelatedFactory will stop
                issuing calls to save(). Refs issues 316 and 366.

.. note:: When any :class:`~factory.RelatedFactory` or :class:`~factory.post_generation`
          attribute is defined on the :class:`~factory.django.DjangoModelFactory` subclass,
          a second ``save()`` is performed *after* the call to ``_create()``.

          Code working with signals should thus use the :meth:`~factory.django.mute_signals` decorator


Simple Many-to-many relationship
--------------------------------

Building the adequate link between two models depends heavily on the use case;
factory_boy doesn't provide a "all in one tools" as for :class:`~factory.SubFactory`
or :class:`~factory.RelatedFactory`, users will have to craft their own depending
on the model.

The base building block for this feature is the :class:`~factory.post_generation`
hook:

.. code-block:: python

    # models.py
    class Group(models.Model):
        name = models.CharField()

    class User(models.Model):
        name = models.CharField()
        groups = models.ManyToManyField(Group)


    # factories.py
    class GroupFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.Group

        name = factory.Sequence(lambda n: "Group #%s" % n)

    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.User

        name = "John Doe"

        @factory.post_generation
        def groups(self, create, extracted, **kwargs):
            if not create or not extracted:
                # Simple build, or nothing to add, do nothing.
                return

            # Add the iterable of groups using bulk addition
            self.groups.add(*extracted)

.. OHAI_VIM**

When calling ``UserFactory()`` or ``UserFactory.build()``, no group binding
will be created.

But when ``UserFactory.create(groups=(group1, group2, group3))`` is called,
the ``groups`` declaration will add passed in groups to the set of groups for the
user.

For SQLAlchemy, change ``self.groups.add(group)`` in the above example to
``self.groups.append(group)``.

Many-to-many relation with a 'through'
--------------------------------------


If only one link is required, this can be simply performed with a :class:`~factory.RelatedFactory`.
If more links are needed, simply add more :class:`~factory.RelatedFactory` declarations:

.. code-block:: python

    # models.py
    class User(models.Model):
        name = models.CharField()

    class Group(models.Model):
        name = models.CharField()
        members = models.ManyToManyField(User, through='GroupLevel')

    class GroupLevel(models.Model):
        user = models.ForeignKey(User)
        group = models.ForeignKey(Group)
        rank = models.IntegerField()


    # factories.py
    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.User

        name = "John Doe"

    class GroupFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.Group

        name = "Admins"

    class GroupLevelFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.GroupLevel

        user = factory.SubFactory(UserFactory)
        group = factory.SubFactory(GroupFactory)
        rank = 1

    class UserWithGroupFactory(UserFactory):
        membership = factory.RelatedFactory(
            GroupLevelFactory,
            factory_related_name='user',
        )

    class UserWith2GroupsFactory(UserFactory):
        membership1 = factory.RelatedFactory(
            GroupLevelFactory,
            factory_related_name='user',
            group__name='Group1',
        )
        membership2 = factory.RelatedFactory(
            GroupLevelFactory,
            factory_related_name='user',
            group__name='Group2',
        )


Whenever the ``UserWithGroupFactory`` is called, it will, as a post-generation hook,
call the ``GroupLevelFactory``, passing the generated user as a ``user`` field:

1. ``UserWithGroupFactory()`` generates a ``User`` instance, ``obj``
2. It calls ``GroupLevelFactory(user=obj)``
3. It returns ``obj``


When using the ``UserWith2GroupsFactory``, that behavior becomes:

1. ``UserWith2GroupsFactory()`` generates a ``User`` instance, ``obj``
2. It calls ``GroupLevelFactory(user=obj, group__name='Group1')``
3. It calls ``GroupLevelFactory(user=obj, group__name='Group2')``
4. It returns ``obj``


Copying fields to a SubFactory
------------------------------

When a field of a related class should match one of the container:


.. code-block:: python

    # models.py
    class Country(models.Model):
        name = models.CharField()
        lang = models.CharField()

    class User(models.Model):
        name = models.CharField()
        lang = models.CharField()
        country = models.ForeignKey(Country)

    class Company(models.Model):
        name = models.CharField()
        owner = models.ForeignKey(User)
        country = models.ForeignKey(Country)


Here, we want:

- The ``User`` to have the ``lang`` of its country (``factory.SelfAttribute('country.lang')``)
- The ``Company`` owner to live in the country of the company (``factory.SelfAttribute('..country')``)

.. code-block:: python

    # factories.py
    class CountryFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.Country

        name = factory.Iterator(["France", "Italy", "Spain"])
        lang = factory.Iterator(['fr', 'it', 'es'])

    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.User

        name = "John"
        lang = factory.SelfAttribute('country.lang')
        country = factory.SubFactory(CountryFactory)

    class CompanyFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.Company

        name = "ACME, Inc."
        country = factory.SubFactory(CountryFactory)
        owner = factory.SubFactory(UserFactory, country=factory.SelfAttribute('..country'))

If the value of a field on the child factory is indirectly derived from a field on the parent factory, you will need to use LazyAttribute and poke the "factory_parent" attribute.

This time, we want the company owner to live in a country neighboring the country of the company:

.. code-block:: python

    class CompanyFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.Company

        name = "ACME, Inc."
        country = factory.SubFactory(CountryFactory)
        owner = factory.SubFactory(UserFactory,
            country=factory.LazyAttribute(lambda o: get_random_neighbor(o.factory_parent.country)))

Custom manager methods
----------------------

Sometimes you need a factory to call a specific manager method other than the
default :meth:`Model.objects.create() <django.db.models.query.QuerySet.create>` method:

.. code-block:: python

   class UserFactory(factory.django.DjangoModelFactory):
       class Meta:
           model = UserenaSignup

       username = "l7d8s"
       email = "my_name@example.com"
       password = "my_password"

       @classmethod
       def _create(cls, model_class, *args, **kwargs):
           """Override the default ``_create`` with our custom call."""
           manager = cls._get_manager(model_class)
           # The default would use ``manager.create(*args, **kwargs)``
           return manager.create_user(*args, **kwargs)


Forcing the sequence counter
----------------------------

A common pattern with factory_boy is to use a :class:`factory.Sequence` declaration
to provide varying values to attributes declared as unique.

However, it is sometimes useful to force a given value to the counter, for instance
to ensure that tests are properly reproducible.

factory_boy provides a few hooks for this:


Forcing the value on a per-call basis
    In order to force the counter for a specific :class:`~factory.Factory` instantiation,
    just pass the value in the ``__sequence=42`` parameter:

    .. code-block:: python

        class AccountFactory(factory.Factory):
            class Meta:
                model = Account
            uid = factory.Sequence(lambda n: n)
            name = "Test"

    .. code-block:: pycon

        >>> obj1 = AccountFactory(name="John Doe", __sequence=10)
        >>> obj1.uid  # Taken from the __sequence counter
        10
        >>> obj2 = AccountFactory(name="Jane Doe")
        >>> obj2.uid  # The base sequence counter hasn't changed
        1


Resetting the counter globally
    If all calls for a factory must start from a deterministic number,
    use :meth:`factory.Factory.reset_sequence`; this will reset the counter
    to its initial value (as defined by :meth:`factory.Factory._setup_next_sequence`).

    .. code-block:: pycon

        >>> AccountFactory().uid
        1
        >>> AccountFactory().uid
        2
        >>> AccountFactory.reset_sequence()
        >>> AccountFactory().uid  # Reset to the initial value
        1
        >>> AccountFactory().uid
        2

    It is also possible to reset the counter to a specific value:

    .. code-block:: pycon

        >>> AccountFactory.reset_sequence(10)
        >>> AccountFactory().uid
        10
        >>> AccountFactory().uid
        11

    This recipe is most useful in a :class:`~unittest.TestCase`'s
    :meth:`~unittest.TestCase.setUp` method.


Forcing the initial value for all projects
    The sequence counter of a :class:`~factory.Factory` can also be set
    automatically upon the first call through the
    :meth:`~factory.Factory._setup_next_sequence` method; this helps when the
    objects' attributes mustn't conflict with preexisting data.

    A typical example is to ensure that running a Python script twice will create
    non-conflicting objects, by setting up the counter to "max used value plus one":

    .. code-block:: python

        class AccountFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.Account

            @classmethod
            def _setup_next_sequence(cls):
                try:
                    return models.Accounts.objects.latest('uid').uid + 1
                except models.Account.DoesNotExist:
                    return 1

    .. code-block:: pycon

        >>> Account.objects.create(uid=42, name="Blah")
        >>> AccountFactory.create()  # Sets up the account number based on the latest uid
        <Account uid=43, name=Test>

.. _recipe-random-management:

Using reproducible randomness
-----------------------------

Although using random values is great, it can provoke test flakiness.
factory_boy provides a few helpers for this.

.. note:: Those methods will seed the random engine used in both :class:`factory.Faker` and :mod:`factory.fuzzy` objects.


Seeding the random engine
    The simplest way to manage randomness is to push a selected seed when starting tests:

    .. code-block:: python

        import factory.random
        # Pass in any value
        factory.random.reseed_random('my awesome project')


Reproducing unseeded tests
    A project might choose not to use an explicit random seed (for better fuzzing),
    but still wishes to have reproducible tests.

    For such cases, use a combination of :meth:`factory.random.get_random_state()`
    and :meth:`factory.random.set_random_state()`.

    Since the random state structure is implementation-specific, we recommend passing it around
    as a base64-encoded pickle dump.

    .. code-block:: python

        class MyTestRunner:

            def setup_test_environment(self):
                state = os.environ.get('TEST_RANDOM_STATE')
                if state:
                    try:
                        decoded_state = pickle.loads(base64.b64decode(state.encode('ascii')))
                    except ValueError:
                        decoded_state = None
                if decoded_state:
                    factory.random.set_random_state(decoded_state)
                else:
                    encoded_state = base64.b64encode(pickle.dumps(factory.random.get_random_state()))
                    print("Current random state: %s" % encoded_state.decode('ascii'))
                super().setup_test_environment()



Converting a factory's output to a dict
---------------------------------------

In order to inject some data to, say, a REST API, it can be useful to fetch the factory's data
as a dict.

Internally, a factory will:

1. Merge declarations and overrides from all sources (class definition, call parameters, ...)
2. Resolve them into a dict
3. Pass that dict as keyword arguments to the model's ``build`` / ``create`` function


In order to get a dict, we'll just have to swap the model; the easiest way is to use
:meth:`factory.build`:

.. code-block:: python

    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.User

        first_name = factory.Sequence(lambda n: "Agent %03d" % n)  # Agent 000, Agent 001, Agent 002
        username = factory.Faker('user_name')

.. code-block:: pycon

    >>> factory.build(dict, FACTORY_CLASS=UserFactory)
    {'first_name': "Agent 000", 'username': 'john_doe'}


Overriding the default locale
-----------------------------

Depending on the needed scope the solution differs slightly, but in any case
you'll most likely need `~factory.Faker.override_default_locale`.

For part of a test:

.. code-block:: python

    def test_something(self):
        ...
        with factory.Faker.override_default_locale('de_DE'):
            ...
        ...

For the whole test:

.. code-block:: python

    @factory.Faker.override_default_locale('de_DE')
    def test_something(self):
        ...

Globally (for all the project's tests):

.. code-block:: python

    # myproject/settings.py
    TEST_RUNNER = 'myproject.testing.MyTestRunner'

    # myproject/testing.py
    import factory
    from django.conf import settings
    from django.util import translation
    import django.test.runner

    class MyTestRunner(django.test.runner.DiscoverRunner):
        def run_tests(self, test_labels, extra_tests=None, **kwargs):
            with factory.Faker.override_default_locale(
                translation.to_locale(settings.LANGUAGE_CODE)
            ):
                return super().run_tests(test_labels, extra_tests=extra_tests, **kwargs)


Fuzzying Django model field choices
-----------------------------------

When defining a :class:`~factory.fuzzy.FuzzyChoice` you can reuse the same choice list from the model field descriptor.

Use the ``getter`` kwarg to select the first element from each choice tuple.

.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = User

        # CATEGORY_CHOICES is a list of (key, title) tuples
        category = factory.fuzzy.FuzzyChoice(User.CATEGORY_CHOICES, getter=lambda c: c[0])


Django models with `GenericForeignKeys`
---------------------------------------

For model which uses `GenericForeignKey <https://docs.djangoproject.com/en/1.10/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey>`_

.. literalinclude:: ../examples/django_demo/generic_foreignkey/models.py

We can create factories like this:

.. literalinclude:: ../examples/django_demo/generic_foreignkey/factories.py
