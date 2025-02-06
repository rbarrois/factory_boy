import inspect
import uuid
from collections.abc import Iterable
import datetime
from decimal import Decimal
from enum import Enum
from typing import Callable, Union, Dict, get_type_hints

from faker import documentor, Faker

import factory
from factory.declarations import BaseDeclaration
from factory.introspector.base import DeclarationMapping, BaseIntrospector, FieldContext
from factory.introspector.utils import enum_declaration, none_declaration


class PythonFakerMappingDeclaration(DeclarationMapping):

    FIELD_TYPE_MAPPING_AUTO_FIELDS: Dict[type, Union[Callable, BaseDeclaration]] = {
        # basic python types
        type(None): lambda ctx: none_declaration(),
        str: factory.Faker("pystr"),
        int: factory.Faker("pyint"),
        float: factory.Faker("pyfloat"),
        bool: factory.Faker("pybool"),
        bytes: factory.Faker("binary"),
        Enum: lambda ctx: enum_declaration(ctx.field.__class__),
        Decimal: factory.Faker("pydecimal"),
        uuid.UUID: factory.Faker("uuid4"),
        # collection types
        list: factory.Faker("pylist"),
        dict: factory.Faker("pydict"),
        tuple: factory.Faker("pytuple"),
        set: factory.Faker("pyset"),
        Iterable: factory.Faker("pyiterable"),
        # date types
        datetime.date: factory.Faker("date"),
        datetime.datetime: factory.Faker("date_time"),
    }

    # Generated once first time an instance is created.
    FIELD_NAME_MAPPING_AUTO_FIELDS: Dict[str, Union[Callable, BaseDeclaration]] = {}

    def __init__(self, custom_field_type_mapping=None, custom_field_name_mapping=None):
        # Generate the field name mapping only once.
        if not self.__class__.FIELD_NAME_MAPPING_AUTO_FIELDS:
            self.__class__.FIELD_NAME_MAPPING_AUTO_FIELDS = self._generate_field_name_mapping()
        super().__init__(
            custom_field_type_mapping=custom_field_type_mapping,
            custom_field_name_mapping=custom_field_name_mapping
        )

    @classmethod
    def _generate_field_name_mapping(cls):
        # Build the formatters mapping only once.
        # Get all the faker formatters.
        provider_mapping = {}
        doc = documentor.Documentor(Faker())
        formatter_list = doc.get_formatters(with_args=False, with_defaults=True, prefix="")
        for formatters in formatter_list:
            # Store the formatter name without the '()' and the type
            # of the formatter example value.
            for name, example in formatters[1].items():
                provider_mapping[name[:-2]] = type(example)
        return provider_mapping


class PythonObjectIntrospector(BaseIntrospector):

    DECLARATION_MAPPING_CLASS = PythonFakerMappingDeclaration

    def __init__(
            self,
            factory_class,
            mapping_strategy_auto_fields=factory.enums.MAPPING_BY_NAME,
            mapping_type_auto_fields=None,
            mapping_name_auto_fields=None,
    ):
        super().__init__(
            factory_class,
            mapping_strategy_auto_fields=mapping_strategy_auto_fields,
            mapping_type_auto_fields=mapping_type_auto_fields,
            mapping_name_auto_fields=mapping_name_auto_fields,
        )
        self.model_type_hints = get_type_hints(self.model)

    def get_default_field_names(self):
        attributes = inspect.getmembers(self.model)
        class_attributes = [a[0] for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
        return set(self.model_type_hints.keys()) | set(class_attributes)

    def get_field_by_name(self, field_name):
        return getattr(self.model, field_name, None)

    def build_field_context(self, field, field_name, sub_skips):
        return FieldContext(
            field=field,
            field_name=field_name,
            field_type=self.model_type_hints.get(field_name, type(None)) if field is None else type(field),
            model=self.model,
            factory=self._factory_class,
            skips=sub_skips,
        )
