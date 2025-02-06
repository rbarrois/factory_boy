import logging
import collections
from abc import ABC, abstractmethod
from difflib import get_close_matches
from typing import Callable, Type, Dict, Union

import factory
from factory import enums
from factory.declarations import BaseDeclaration

logger = logging.getLogger(__name__)

FieldContext = collections.namedtuple(
    "FieldContext", ["field", "field_name", "field_type", "model", "factory", "skips"]
)


class DeclarationMapping(ABC):
    @property
    @abstractmethod
    def FIELD_TYPE_MAPPING_AUTO_FIELDS(self) -> Dict[type, Union[Callable, BaseDeclaration]]:
        pass

    @property
    @abstractmethod
    def FIELD_NAME_MAPPING_AUTO_FIELDS(self) -> Dict[str, Union[Callable, BaseDeclaration]]:
        pass

    def __init__(self, custom_field_type_mapping=None, custom_field_name_mapping=None):
        self.field_type_mapping = dict(self.FIELD_TYPE_MAPPING_AUTO_FIELDS)
        self.field_name_mapping = dict(self.FIELD_NAME_MAPPING_AUTO_FIELDS)
        if custom_field_type_mapping:
            self.field_type_mapping.update(custom_field_type_mapping)
        if custom_field_name_mapping:
            self.field_name_mapping.update(custom_field_name_mapping)

    def get_by_field_name(self, field_name, field_type):
        """Get the mapped declaration based on the field name.
        The field type is here only to check if the declaration returns the same
        type as the field is expected to get.
        The matching by field name is done with the python difflib library.
        This method can be overridden to customize the field name search algorithm.

        Args:
            field_name (str): the field name to search in the mapping
            field_type (type): the type of the field

        Returns:
            The declaration or a callable returning a declaration found
            inside the declared mapping in `FIELD_NAME_MAPPING_AUTO_FIELDS`.
        """
        formatter_name = None
        # Get the closest match according to the name
        # and the type of the formatter value.
        closest_matches = get_close_matches(
            field_name, self.field_name_mapping.keys(), n=3, cutoff=0.6
        )
        if closest_matches:
            # Check type is matching
            for closest_match in closest_matches:
                if self.field_name_mapping[closest_match] == field_type:
                    formatter_name = factory.Faker(closest_match)
                    break
        return formatter_name

    def get_by_field_type(self, field_type):
        """Get the mapped declaration based on the field type.

        Args:
           field_type (type): the type of the field
        Returns:

            The declaration or a callable returning a declaration found
            inside the declared mapping in `FIELD_TYPE_MAPPING_AUTO_FIELDS`.
        """
        return self.field_type_mapping.get(field_type)


class BaseIntrospector(ABC):
    """Introspector for models.

    Extracts declarations from a model.
    """

    DECLARATION_MAPPING_CLASS: Type[DeclarationMapping] = None

    def __init__(
        self,
        factory_class,
        mapping_strategy_auto_fields=enums.MAPPING_BY_NAME,
        mapping_type_auto_fields=None,
        mapping_name_auto_fields=None,
    ):
        self._factory_class = factory_class
        self.model = self._factory_class._meta.model
        self.declaration_mapping = self.DECLARATION_MAPPING_CLASS(
            custom_field_type_mapping=mapping_type_auto_fields,
            custom_field_name_mapping=mapping_name_auto_fields,
        )
        self.mapping_strategy_auto_fields = mapping_strategy_auto_fields

    @abstractmethod
    def get_default_field_names(self):
        """
        Fetch default "auto-declarable" field names from a model.
        Override to define what fields are included by default
        """
        raise NotImplementedError(
            "Introspector %r doesn't know how to extract fields from %s" % (self, model)
        )

    @abstractmethod
    def get_field_by_name(self, field_name):
        """
        Get the actual "field descriptor" for a given field name
        Actual return value will depend on your underlying lib
        May return None if the field does not exist
        """
        raise NotImplementedError(
            "Introspector %r doesn't know how to fetch field %s from %r"
            % (self._factory_class, field_name, self.model)
        )

    def build_declaration(self, field_context):
        """Build a factory.Declaration from a FieldContext

        Note that FieldContext may be None if get_field_by_name() returned None

        Returns:
            factory.Declaration
        """
        field_type = field_context.field_type
        field_name = field_context.field_name
        declaration_by_name = None
        declaration_by_type = self.declaration_mapping.get_by_field_type(field_type)
        if self.mapping_strategy_auto_fields == enums.MAPPING_BY_NAME:
            declaration_by_name = self.declaration_mapping.get_by_field_name(
                field_name, field_type
            )
        mapped_declaration = (
            declaration_by_name if declaration_by_name else declaration_by_type
        )

        if mapped_declaration is None:
            raise NotImplementedError(
                "Introspector {} lacks mapping for building field {} (type: {}). "
                "Add it to {}.Meta.custom_mapping_auto_fields.".format(
                    self, field_name, field_type, self._factory_class.__name__
                )
            )

        # A callable can be passed, evaluate it and make sure it returns a declaration.
        if isinstance(mapped_declaration, Callable):
            mapped_declaration = mapped_declaration(field_context)

        if not isinstance(mapped_declaration, BaseDeclaration):
            raise ValueError(
                "The related mapping of field {} (type: {}) must be a callable or a declaration. "
                "Type {} is not supported.".format(
                    field_name, field_type, type(mapped_declaration)
                )
            )
        return mapped_declaration

    def build_declarations(self, fields_names, skip_fields_names):
        """Build declarations for a set of fields.

        Args:
            fields_names (str iterable): list of fields to build
            skip_fields_names (str iterable): list of fields that should *NOT* be built.

        Returns:
            (str, factory.Declaration) dict: the new declarations.
        """
        declarations = {}
        for field_name in fields_names:
            if field_name in skip_fields_names:
                continue

            sub_skip_pattern = "%s__" % field_name
            sub_skips = [
                sk[len(sub_skip_pattern) :]
                for sk in skip_fields_names
                if sk.startswith(sub_skip_pattern)
            ]

            field = self.get_field_by_name(field_name)

            field_ctxt = self.build_field_context(field, field_name, sub_skips)
            declaration = self.build_declaration(field_ctxt)
            if declaration is not None:
                declarations[field_name] = declaration

        return declarations

    def build_field_context(self, field, field_name, sub_skips):
        return FieldContext(
            field=field,
            field_name=field_name,
            field_type=type(field),
            model=self.model,
            factory=self._factory_class,
            skips=sub_skips,
        )

    def __repr__(self):
        return "<%s for %s>" % (self.__class__.__name__, self._factory_class.__name__)
