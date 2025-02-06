import unittest
from datetime import datetime

from factory.introspector.python_object import PythonFakerMappingDeclaration, PythonObjectIntrospector
from factory.python_object import PythonModelFactory


class TestPythonFakerMappingDeclaration(unittest.TestCase):
    def test_guess_formatter_with_exact_name(self):
        self.assertEqual(
            PythonFakerMappingDeclaration().get_by_field_name("city", str).provider,
            "city",
        )

    def test_guess_formatter_only_preffix(self):
        self.assertEqual(
            PythonFakerMappingDeclaration()
            .get_by_field_name("secondary", str)
            .provider,
            "secondary_address",
        )

    def test_guess_formatter_only_suffix(self):
        self.assertEqual(
            PythonFakerMappingDeclaration().get_by_field_name("last", str).provider,
            "last_name",
        )

    def test_guess_formatter_only_middle(self):
        self.assertEqual(
            PythonFakerMappingDeclaration()
            .get_by_field_name("phonenumber", str)
            .provider,
            "phone_number",
        )

    def test_guess_formatter_type_matching(self):
        self.assertEqual(
            PythonFakerMappingDeclaration().get_by_field_name("bin", bytes).provider,
            "binary",
        )

    def test_guess_formatter_type_not_matching(self):
        self.assertEqual(
            PythonFakerMappingDeclaration().get_by_field_name("profile", str).provider,
            "prefix_male",
        )

    def test_guess_formatter_type_dict_matching(self):
        self.assertEqual(
            PythonFakerMappingDeclaration().get_by_field_name("profil", dict).provider,
            "profile",
        )


class PythonObject:
    a = 1
    b = ""
    c: datetime

    def __init__(self, a=None, b=None, c=None):
        self.a = a
        self.b = b
        self.c = c


class ObjectFactory(PythonModelFactory):
    class Meta:
        model = PythonObject


class TestPythonObjectIntrospector(unittest.TestCase):

    def test_get_default_field_names(self):
        self.assertEqual(
           PythonObjectIntrospector(ObjectFactory).get_default_field_names(),
            {"a", "b", "c"}
        )

    def test_get_field_by_name(self):
        self.assertEqual(
           PythonObjectIntrospector(ObjectFactory).get_field_by_name("a"),
           PythonObject.a
        )

    def test_concrete_factory(self):
        class ObjectFactory(PythonModelFactory):
            class Meta:
                model = PythonObject
                default_auto_fields = True

        python_object_instance = ObjectFactory()
        self.assertEqual(type(python_object_instance.a), int)
        self.assertEqual(type(python_object_instance.b), str)
        self.assertEqual(type(python_object_instance.c), datetime)
