import unittest

import factory
from factory import base, enums
from factory.introspector.base import FieldContext, BaseIntrospector, DeclarationMapping


class Model:
    field: str = ""
    field_2: str = ""


class ChildModel(Model):
    child_field: str = ""


class ModelFactory(base.Factory):
    class Meta:
        model = Model


class ChildModelFactory(ModelFactory):
    class Meta:
        model = ChildModel


class BasicMapping(DeclarationMapping):

    FIELD_TYPE_MAPPING_AUTO_FIELDS = {str: factory.Faker("pystr")}
    FIELD_NAME_MAPPING_AUTO_FIELDS = {}


class Interpretor(BaseIntrospector):

    DECLARATION_MAPPING_CLASS = BasicMapping

    def get_default_field_names(self):
        return ["field", "field_2"]

    def get_field_by_name(self, field_name):
        return getattr(self.model, field_name, None)


class ChildInterpretor(Interpretor):

    def get_default_field_names(self):
        return super().get_default_field_names() + ["child_field"]


class TestBaseIntrospector(unittest.TestCase):
    def test_build_declaration(self):
        model = Model()
        model_factory_class = ModelFactory
        field_ctxt = FieldContext(
            field=model.field,
            field_name="field",
            field_type=type(model.field),
            model=model,
            factory=model_factory_class,
            skips=[],
        )
        self.assertEqual(
            Interpretor(model_factory_class).build_declaration(field_ctxt).provider,
            "pystr",
        )

    def test_build_declaration_with_overridden_mapping(self):
        model = Model()
        model_factory_class = ModelFactory
        field_ctxt = FieldContext(
            field=model.field,
            field_name="field",
            field_type=type(model.field),
            model=model,
            factory=model_factory_class,
            skips=[],
        )
        self.assertEqual(
            Interpretor(
                model_factory_class,
                mapping_strategy_auto_fields=enums.MAPPING_BY_TYPE,
                mapping_type_auto_fields={str: factory.Faker("first_name")}
            )
            .build_declaration(field_ctxt)
            .provider,
            "first_name",
        )

    def test_build_declaration_with_overridden_mapping_not_impacting_default(self):
        model = Model()
        model_factory_class = ModelFactory
        field_ctxt = FieldContext(
            field=model.field,
            field_name="field",
            field_type=type(model.field),
            model=model,
            factory=model_factory_class,
            skips=[],
        )
        self.assertEqual(
            Interpretor(
                model_factory_class,
                mapping_strategy_auto_fields=enums.MAPPING_BY_TYPE,
                mapping_type_auto_fields={int: factory.Faker("pyint")}
            )
            .build_declaration(field_ctxt)
            .provider,
            "pystr",
        )

    def test_build_declaration_no_mapping_set(self):
        model = Model()
        model_factory_class = ModelFactory
        field_ctxt = FieldContext(
            field=1,
            field_name="field",
            field_type=int,
            model=model,
            factory=model_factory_class,
            skips=[],
        )
        with self.assertRaises(NotImplementedError):
            Interpretor(model_factory_class).build_declaration(field_ctxt)

    def test_build_declarations(self):
        model_factory_class = ModelFactory
        declarations = Interpretor(model_factory_class).build_declarations(
            ["field"], []
        )
        self.assertEqual(len(declarations), 1)
        self.assertEqual(declarations["field"].provider, "pystr")

    def test_build_declarations_with_skip(self):
        model_factory_class = ModelFactory
        declarations = Interpretor(model_factory_class).build_declarations(
            ["field"], ["field"]
        )
        self.assertEqual(len(declarations), 0)

    def test_build_declarations_with_skip_on_parent_factory_field(self):
        model_factory_class = ChildModelFactory
        declarations = Interpretor(model_factory_class).build_declarations(
            ["field", "field_2", "child_field"], ["field_2"]
        )
        self.assertEqual(len(declarations), 2)
