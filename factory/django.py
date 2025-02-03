# Copyright: See the LICENSE file.


"""factory_boy extensions for use with the Django framework."""


import functools
import io
import logging
import os
import warnings
from collections import defaultdict
from typing import Dict, TypeVar

from django.contrib.auth.hashers import make_password
from django.core import files as django_files
from django.db import IntegrityError, connections, models
from django.db.models.sql import InsertQuery

from . import base, builder, declarations, enums, errors

logger = logging.getLogger('factory.generate')

DEFAULT_DB_ALIAS = 'default'  # Same as django.db.DEFAULT_DB_ALIAS
T = TypeVar("T")
_LAZY_LOADS: Dict[str, object] = {}


def get_model(app, model):
    """Wrapper around django's get_model."""
    if 'get_model' not in _LAZY_LOADS:
        _lazy_load_get_model()

    _get_model = _LAZY_LOADS['get_model']
    return _get_model(app, model)


def _lazy_load_get_model():
    """Lazy loading of get_model.

    get_model loads django.conf.settings, which may fail if
    the settings haven't been configured yet.
    """
    from django import apps as django_apps
    _LAZY_LOADS['get_model'] = django_apps.apps.get_model


def connection_supports_bulk_insert(using):
    """
    Does the database support bulk_insert

    There are 2 pieces to this puzzle:
      * The database needs to support `bulk_insert`
      * AND it also needs to be capable of returning all the newly minted objects' id

    If any of these is `False`, the database does NOT support bulk_insert
    """
    db_features = connections[using].features
    return (
        db_features.has_bulk_insert
        and db_features.can_return_rows_from_bulk_insert
    )


class DjangoOptions(base.FactoryOptions):
    def _build_default_options(self):
        return super()._build_default_options() + [
            base.OptionDefault('django_get_or_create', (), inherit=True),
            base.OptionDefault('database', DEFAULT_DB_ALIAS, inherit=True),
            base.OptionDefault('use_bulk_create', False, inherit=True),
            base.OptionDefault('skip_postgeneration_save', False, inherit=True),
        ]

    def _get_counter_reference(self):
        counter_reference = super()._get_counter_reference()
        if (counter_reference == self.base_factory
                and self.base_factory._meta.model is not None
                and self.base_factory._meta.model._meta.abstract
                and self.model is not None
                and not self.model._meta.abstract):
            # Target factory is for an abstract model, yet we're for another,
            # concrete subclass => don't reuse the counter.
            return self.factory
        return counter_reference

    def get_model_class(self):
        if isinstance(self.model, str) and '.' in self.model:
            app, model_name = self.model.split('.', 1)
            self.model = get_model(app, model_name)

        return self.model


class DjangoModelFactory(base.Factory[T]):
    """Factory for Django models.

    This makes sure that the 'sequence' field of created objects is a new id.

    Possible improvement: define a new 'attribute' type, AutoField, which would
    handle those for non-numerical primary keys.
    """

    _options_class = DjangoOptions
    _original_params = None

    class Meta:
        abstract = True  # Optional, but explicit.

    @classmethod
    def _load_model_class(cls, definition):

        if isinstance(definition, str) and '.' in definition:
            app, model = definition.split('.', 1)
            return get_model(app, model)

        return definition

    @classmethod
    def _get_manager(cls, model_class):
        if model_class is None:
            raise errors.AssociatedClassError(
                f"No model set on {cls.__module__}.{cls.__name__}.Meta")

        try:
            manager = model_class.objects
        except AttributeError:
            # When inheriting from an abstract model with a custom
            # manager, the class has no 'objects' field.
            manager = model_class._default_manager

        if cls._meta.database != DEFAULT_DB_ALIAS:
            manager = manager.using(cls._meta.database)
        return manager

    @classmethod
    def _generate(cls, strategy, params):
        # Original params are used in _get_or_create if it cannot build an
        # object initially due to an IntegrityError being raised
        cls._original_params = params
        return super()._generate(strategy, params)

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        """Create an instance of the model through objects.get_or_create."""
        manager = cls._get_manager(model_class)

        assert 'defaults' not in cls._meta.django_get_or_create, (
            "'defaults' is a reserved keyword for get_or_create "
            "(in %s._meta.django_get_or_create=%r)"
            % (cls, cls._meta.django_get_or_create))

        key_fields = {}
        for field in cls._meta.django_get_or_create:
            if field not in kwargs:
                raise errors.FactoryError(
                    "django_get_or_create - "
                    "Unable to find initialization value for '%s' in factory %s" %
                    (field, cls.__name__))
            key_fields[field] = kwargs.pop(field)
        key_fields['defaults'] = kwargs

        try:
            instance, _created = manager.get_or_create(*args, **key_fields)
        except IntegrityError as e:

            if cls._original_params is None:
                raise e

            get_or_create_params = {
                lookup: value
                for lookup, value in cls._original_params.items()
                if lookup in cls._meta.django_get_or_create
            }
            if get_or_create_params:
                try:
                    instance = manager.get(**get_or_create_params)
                except manager.model.DoesNotExist:
                    # Original params are not a valid lookup and triggered a create(),
                    # that resulted in an IntegrityError. Follow Django’s behavior.
                    raise e
            else:
                raise e

        return instance

    @classmethod
    def supports_bulk_insert(cls):
        return (cls._meta.use_bulk_create
                and connection_supports_bulk_insert(cls._meta.database))

    @classmethod
    def create(cls, **kwargs):
        """Create an instance of the associated class, with overridden attrs."""
        if not cls.supports_bulk_insert():
            return super().create(**kwargs)

        return cls._bulk_create(1, **kwargs)[0]

    @classmethod
    def create_batch(cls, size, **kwargs):
        if not cls.supports_bulk_insert():
            return super().create_batch(size, **kwargs)

        return cls._bulk_create(size, **kwargs)

    @classmethod
    def _refresh_database_pks(cls, model_cls, objs):
        # Avoid causing a django.core.exceptions.AppRegistryNotReady throughout all the tests.
        # TODO: remove the `from . import django` from the `__init__.py`
        from django.contrib.contenttypes.fields import GenericForeignKey

        def get_field_value(instance, field):
            if isinstance(field, GenericForeignKey) and field.is_cached(instance):
                return field.get_cached_value(instance)
            return getattr(instance, field.name)

        # Current Django version's GenericForeignKey is not made to work with bulk_insert.
        #
        # The issue is that it caches the object referenced, once the object is
        # saved and receives a pk, the cache no longer matches. It doesn't
        # matter that it's the same obj reference. This is to bypass that pk
        # check and reset it.
        fields_to_reset = (GenericForeignKey, models.OneToOneField)

        fields = [f for f in model_cls._meta.get_fields() if isinstance(f, fields_to_reset)]
        if not fields:
            return

        for obj in objs:
            for field in fields:
                setattr(obj, field.name, get_field_value(obj, field))

    @classmethod
    def _bulk_create(cls, size, **kwargs):
        if cls._meta.abstract:
            raise errors.FactoryError(
                "Cannot generate instances of abstract factory %(f)s; "
                "Ensure %(f)s.Meta.model is set and %(f)s.Meta.abstract "
                "is either not set or False." % dict(f=cls.__name__))

        models_to_return = []
        instances = []
        for _ in range(size):
            step = builder.StepBuilder(cls._meta, kwargs, enums.BUILD_STRATEGY)
            models_to_return.append(step.build(collect_instances=instances))

        for model_cls, objs in dependency_insert_order(instances):
            manager = cls._get_manager(model_cls)
            cls._refresh_database_pks(model_cls, objs)

            concrete_model = True
            for parent in model_cls._meta.get_parent_list():
                if parent._meta.concrete_model is not model_cls._meta.concrete_model:
                    concrete_model = False

            if concrete_model:
                manager.bulk_create(objs)
            else:
                concrete_fields = model_cls._meta.local_fields
                connection = connections[cls._meta.database]

                # Avoids writing the INSERT INTO sql script manually
                query = InsertQuery(model_cls)
                query.insert_values(concrete_fields, objs)
                query.get_compiler(connection=connection).execute_sql()

        return models_to_return

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        if cls._meta.django_get_or_create:
            return cls._get_or_create(model_class, *args, **kwargs)

        manager = cls._get_manager(model_class)
        return manager.create(*args, **kwargs)

    # DEPRECATED. Remove this override with the next major release.
    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results and not cls._meta.skip_postgeneration_save:
            warnings.warn(
                f"{cls.__name__}._after_postgeneration will stop saving the instance "
                "after postgeneration hooks in the next major release.\n"
                "If the save call is extraneous, set skip_postgeneration_save=True "
                f"in the {cls.__name__}.Meta.\n"
                "To keep saving the instance, move the save call to your "
                "postgeneration hooks or override _after_postgeneration.",
                DeprecationWarning,
            )
            # Some post-generation hooks ran, and may have modified us.
            instance.save()


class Password(declarations.Transformer):
    def __init__(self, password, transform=make_password, **kwargs):
        super().__init__(password, transform=transform, **kwargs)


class FileField(declarations.BaseDeclaration):
    """Helper to fill in django.db.models.FileField from a Factory."""

    DEFAULT_FILENAME = 'example.dat'

    def _make_data(self, params):
        """Create data for the field."""
        return params.get('data', b'')

    def _make_content(self, params):
        path = ''

        from_path = params.get('from_path')
        from_file = params.get('from_file')
        from_func = params.get('from_func')

        if len([p for p in (from_path, from_file, from_func) if p]) > 1:
            raise ValueError(
                "At most one argument from 'from_file', 'from_path', and 'from_func' should "
                "be non-empty when calling factory.django.FileField."
            )

        if from_path:
            path = from_path
            with open(path, 'rb') as f:
                content = django_files.base.ContentFile(f.read())

        elif from_file:
            f = from_file
            content = django_files.File(f)
            path = content.name

        elif from_func:
            func = from_func
            content = django_files.File(func())
            path = content.name

        else:
            data = self._make_data(params)
            content = django_files.base.ContentFile(data)

        if path:
            default_filename = os.path.basename(path)
        else:
            default_filename = self.DEFAULT_FILENAME

        filename = params.get('filename', default_filename)
        return filename, content

    def evaluate(self, instance, step, extra):
        """Fill in the field."""
        filename, content = self._make_content(extra)
        return django_files.File(content.file, filename)


class ImageField(FileField):
    DEFAULT_FILENAME = 'example.jpg'

    def _make_data(self, params):
        # ImageField (both django's and factory_boy's) require PIL.
        # Try to import it along one of its known installation paths.
        from PIL import Image

        width = params.get('width', 100)
        height = params.get('height', width)
        color = params.get('color', 'blue')
        image_format = params.get('format', 'JPEG')
        image_palette = params.get('palette', 'RGB')

        thumb_io = io.BytesIO()
        with Image.new(image_palette, (width, height), color) as thumb:
            thumb.save(thumb_io, format=image_format)
        return thumb_io.getvalue()


def dependency_insert_order(data):
    """This is almost the same function from django/core/serializers/__init__.py:sort_dependencies with a slight
    modification on `if hasattr(rel_model, 'natural_key') and rel_model != model:` that was removed, so we have the
    REAL dependency order. The original implementation was setup to only write to fields in order if they had a known
    dependency, we always want it in order regardless of the natural_key.
    """

    lookup = []
    model_cls_by_data = defaultdict(list)
    for instance in data:
        # Instance has been persisted in the database
        if not instance._state.adding:
            continue
        # Instance already in the list
        if id(instance) in lookup:
            continue
        model_cls_by_data[type(instance)].append(instance)

    # Avoid data leaks
    del lookup
    del data

    # Process the list of models, and get the list of dependencies
    model_dependencies = []
    models = list(model_cls_by_data.keys())

    for model in models:
        deps = set()

        # Now add a dependency for any FK relation with a model that
        # defines a natural key
        for field in model._meta.fields:
            rel_model = field.related_model
            if rel_model and rel_model != model:
                deps.add(rel_model)

        model_dependencies.append((model, deps))

    model_dependencies.reverse()
    # Now sort the models to ensure that dependencies are met. This
    # is done by repeatedly iterating over the input list of models.
    # If all the dependencies of a given model are in the final list,
    # that model is promoted to the end of the final list. This process
    # continues until the input list is empty, or we do a full iteration
    # over the input models without promoting a model to the final list.
    # If we do a full iteration without a promotion, that means there are
    # circular dependencies in the list.
    model_list = []
    while model_dependencies:
        skipped = []
        changed = False
        while model_dependencies:
            model, deps = model_dependencies.pop()

            # If all of the models in the dependency list are either already
            # on the final model list, or not on the original serialization list,
            # then we've found another model with all it's dependencies satisfied.
            found = True
            for candidate in ((d not in models or d in model_list) for d in deps):
                if not candidate:
                    found = False
            if found:
                model_list.append(model)
                changed = True
            else:
                skipped.append((model, deps))
        if not changed:
            unresolved_models = (f'{model._meta.app_label}.{model._meta.object_name}'
                                 for model, _ in sorted(skipped, key=lambda obj: obj[0].__name__))
            message = f"Can't resolve dependencies for {', '.join(unresolved_models)}."
            raise RuntimeError(message)
        model_dependencies = skipped

    return [(model_cls, model_cls_by_data[model_cls]) for model_cls in model_list]


class mute_signals:
    """Temporarily disables and then restores any django signals.

    Args:
        *signals (django.dispatch.dispatcher.Signal): any django signals

    Examples:
        with mute_signals(pre_init):
            user = UserFactory.build()
            ...

        @mute_signals(pre_save, post_save)
        class UserFactory(factory.Factory):
            ...

        @mute_signals(post_save)
        def generate_users():
            UserFactory.create_batch(10)
    """

    def __init__(self, *signals):
        self.signals = signals
        self.paused = {}

    def __enter__(self):
        for signal in self.signals:
            logger.debug('mute_signals: Disabling signal handlers %r',
                         signal.receivers)

            # Note that we're using implementation details of
            # django.signals, since arguments to signal.connect()
            # are lost in signal.receivers
            self.paused[signal] = signal.receivers
            signal.receivers = []

    def __exit__(self, exc_type, exc_value, traceback):
        for signal, receivers in self.paused.items():
            logger.debug('mute_signals: Restoring signal handlers %r',
                         receivers)

            signal.receivers = receivers + signal.receivers
            with signal.lock:
                # Django uses some caching for its signals.
                # Since we're bypassing signal.connect and signal.disconnect,
                # we have to keep messing with django's internals.
                signal.sender_receivers_cache.clear()
        self.paused = {}

    def copy(self):
        return mute_signals(*self.signals)

    def __call__(self, callable_obj):
        if isinstance(callable_obj, base.FactoryMetaClass):
            # Retrieve __func__, the *actual* callable object.
            callable_obj._create = self.wrap_method(callable_obj._create.__func__)
            callable_obj._bulk_create = self.wrap_method(callable_obj._bulk_create.__func__)
            callable_obj._generate = self.wrap_method(callable_obj._generate.__func__)
            callable_obj._after_postgeneration = self.wrap_method(
                callable_obj._after_postgeneration.__func__
            )
            return callable_obj

        else:
            @functools.wraps(callable_obj)
            def wrapper(*args, **kwargs):
                # A mute_signals() object is not reentrant; use a copy every time.
                with self.copy():
                    return callable_obj(*args, **kwargs)
            return wrapper

    def wrap_method(self, method):
        @classmethod
        @functools.wraps(method)
        def wrapped_method(*args, **kwargs):
            # A mute_signals() object is not reentrant; use a copy every time.
            with self.copy():
                return method(*args, **kwargs)
        return wrapped_method
