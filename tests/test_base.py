# Copyright: See the LICENSE file.

import unittest

from factory import base, declarations, enums, errors


class TestObject:
    def __init__(self, one=None, two=None, three=None, four=None):
        self.one = one
        self.two = two
        self.three = three
        self.four = four


class FakeDjangoModel:
    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.id = 1
        return instance

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
            self.id = None


class FakeModelFactory(base.Factory):
    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.create(**kwargs)


class TestModel(FakeDjangoModel):
    pass


class SafetyTestCase(unittest.TestCase):
    def test_base_factory(self):
        with self.assertRaises(errors.FactoryError):
            base.BaseFactory()


class AbstractFactoryTestCase(unittest.TestCase):
    def test_factory_for_optional(self):
        """Ensure that model= is optional for abstract=True."""
        class TestObjectFactory(base.Factory):
            class Meta:
                abstract = True

        self.assertTrue(TestObjectFactory._meta.abstract)
        self.assertIsNone(TestObjectFactory._meta.model)

    def test_factory_for_and_abstract_factory_optional(self):
        """Ensure that Meta.abstract is optional."""
        class TestObjectFactory(base.Factory):
            pass

        self.assertTrue(TestObjectFactory._meta.abstract)
        self.assertIsNone(TestObjectFactory._meta.model)

    def test_abstract_factory_cannot_be_called(self):
        class TestObjectFactory(base.Factory):
            pass

        with self.assertRaises(errors.FactoryError):
            TestObjectFactory.build()
        with self.assertRaises(errors.FactoryError):
            TestObjectFactory.create()

    def test_abstract_factory_not_inherited(self):
        """abstract=True isn't propagated to child classes."""

        class TestObjectFactory(base.Factory):
            class Meta:
                abstract = True
                model = TestObject

        class TestObjectChildFactory(TestObjectFactory):
            pass

        self.assertFalse(TestObjectChildFactory._meta.abstract)

    def test_abstract_or_model_is_required(self):
        class TestObjectFactory(base.Factory):
            class Meta:
                abstract = False
                model = None

        with self.assertRaises(errors.FactoryError):
            TestObjectFactory.build()
        with self.assertRaises(errors.FactoryError):
            TestObjectFactory.create()


class OptionsTests(unittest.TestCase):
    def test_base_attrs(self):
        class AbstractFactory(base.Factory):
            pass

        # Declarative attributes
        self.assertTrue(AbstractFactory._meta.abstract)
        self.assertIsNone(AbstractFactory._meta.model)
        self.assertEqual((), AbstractFactory._meta.inline_args)
        self.assertEqual((), AbstractFactory._meta.exclude)
        self.assertEqual(enums.CREATE_STRATEGY, AbstractFactory._meta.strategy)

        # Non-declarative attributes
        self.assertEqual({}, AbstractFactory._meta.pre_declarations.as_dict())
        self.assertEqual({}, AbstractFactory._meta.post_declarations.as_dict())
        self.assertEqual(AbstractFactory, AbstractFactory._meta.factory)
        self.assertEqual(base.Factory, AbstractFactory._meta.base_factory)
        self.assertEqual(AbstractFactory._meta, AbstractFactory._meta.counter_reference)

    def test_declaration_collecting(self):
        lazy = declarations.LazyFunction(int)
        lazy2 = declarations.LazyAttribute(lambda _o: 1)
        postgen = declarations.PostGenerationDeclaration()

        class AbstractFactory(base.Factory):
            x = 1
            y = lazy
            y2 = lazy2
            z = postgen

        # Declarations aren't removed
        self.assertEqual(1, AbstractFactory.x)
        self.assertEqual(lazy, AbstractFactory.y)
        self.assertEqual(lazy2, AbstractFactory.y2)
        self.assertEqual(postgen, AbstractFactory.z)

        # And are available in class Meta
        self.assertEqual(
            {'x': 1, 'y': lazy, 'y2': lazy2},
            AbstractFactory._meta.pre_declarations.as_dict(),
        )
        self.assertEqual(
            {'z': postgen},
            AbstractFactory._meta.post_declarations.as_dict(),
        )

    def test_inherited_declaration_collecting(self):
        lazy = declarations.LazyFunction(int)
        lazy2 = declarations.LazyAttribute(lambda _o: 2)
        postgen = declarations.PostGenerationDeclaration()
        postgen2 = declarations.PostGenerationDeclaration()

        class AbstractFactory(base.Factory):
            x = 1
            y = lazy
            z = postgen

        class OtherFactory(AbstractFactory):
            a = lazy2
            b = postgen2

        # Declarations aren't removed
        self.assertEqual(lazy2, OtherFactory.a)
        self.assertEqual(postgen2, OtherFactory.b)
        self.assertEqual(1, OtherFactory.x)
        self.assertEqual(lazy, OtherFactory.y)
        self.assertEqual(postgen, OtherFactory.z)

        # And are available in class Meta
        self.assertEqual(
            {'x': 1, 'y': lazy, 'a': lazy2},
            OtherFactory._meta.pre_declarations.as_dict(),
        )
        self.assertEqual(
            {'z': postgen, 'b': postgen2},
            OtherFactory._meta.post_declarations.as_dict(),
        )

    def test_inherited_declaration_shadowing(self):
        lazy = declarations.LazyFunction(int)
        lazy2 = declarations.LazyAttribute(lambda _o: 2)
        postgen = declarations.PostGenerationDeclaration()
        postgen2 = declarations.PostGenerationDeclaration()

        class AbstractFactory(base.Factory):
            x = 1
            y = lazy
            z = postgen

        class OtherFactory(AbstractFactory):
            y = lazy2
            z = postgen2

        # Declarations aren't removed
        self.assertEqual(1, OtherFactory.x)
        self.assertEqual(lazy2, OtherFactory.y)
        self.assertEqual(postgen2, OtherFactory.z)

        # And are available in class Meta
        self.assertEqual(
            {'x': 1, 'y': lazy2},
            OtherFactory._meta.pre_declarations.as_dict(),
        )
        self.assertEqual(
            {'z': postgen2},
            OtherFactory._meta.post_declarations.as_dict(),
        )

    def test_factory_as_meta_model_raises_exception(self):
        class FirstFactory(base.Factory):
            pass

        class Meta:
            model = FirstFactory

        with self.assertRaises(TypeError):
            type("SecondFactory", (base.Factory,), {"Meta": Meta})


class DeclarationParsingTests(unittest.TestCase):
    def test_classmethod(self):
        class TestObjectFactory(base.Factory):
            class Meta:
                model = TestObject

            @classmethod
            def some_classmethod(cls):
                return cls.create()

        self.assertTrue(hasattr(TestObjectFactory, 'some_classmethod'))
        obj = TestObjectFactory.some_classmethod()
        self.assertEqual(TestObject, obj.__class__)


class FactoryTestCase(unittest.TestCase):
    def test_magic_happens(self):
        """Calling a FooFactory doesn't yield a FooFactory instance."""
        class TestObjectFactory(base.Factory):
            class Meta:
                model = TestObject

        self.assertEqual(TestObject, TestObjectFactory._meta.model)
        obj = TestObjectFactory.build()
        self.assertFalse(hasattr(obj, '_meta'))

    def test_display(self):
        class TestObjectFactory(base.Factory):
            class Meta:
                model = FakeDjangoModel

        self.assertIn('TestObjectFactory', str(TestObjectFactory))
        self.assertIn('FakeDjangoModel', str(TestObjectFactory))

    def test_lazy_attribute_non_existent_param(self):
        class TestObjectFactory(base.Factory):
            class Meta:
                model = TestObject

            one = declarations.LazyAttribute(lambda a: a.does_not_exist)

        with self.assertRaises(AttributeError):
            TestObjectFactory()

    def test_inheritance_with_sequence(self):
        """Tests that sequence IDs are shared between parent and son."""
        class TestObjectFactory(base.Factory):
            class Meta:
                model = TestObject

            one = declarations.Sequence(lambda a: a)

        class TestSubFactory(TestObjectFactory):
            class Meta:
                model = TestObject

            pass

        parent = TestObjectFactory.build()
        sub = TestSubFactory.build()
        alt_parent = TestObjectFactory.build()
        alt_sub = TestSubFactory.build()
        ones = {x.one for x in (parent, alt_parent, sub, alt_sub)}
        self.assertEqual(4, len(ones))


class FactorySequenceTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        class TestObjectFactory(base.Factory):
            class Meta:
                model = TestObject
            one = declarations.Sequence(lambda n: n)

        self.TestObjectFactory = TestObjectFactory

    def test_reset_sequence(self):
        o1 = self.TestObjectFactory()
        self.assertEqual(0, o1.one)

        o2 = self.TestObjectFactory()
        self.assertEqual(1, o2.one)

        self.TestObjectFactory.reset_sequence()
        o3 = self.TestObjectFactory()
        self.assertEqual(0, o3.one)

    def test_reset_sequence_with_value(self):
        o1 = self.TestObjectFactory()
        self.assertEqual(0, o1.one)

        o2 = self.TestObjectFactory()
        self.assertEqual(1, o2.one)

        self.TestObjectFactory.reset_sequence(42)
        o3 = self.TestObjectFactory()
        self.assertEqual(42, o3.one)

    def test_reset_sequence_subclass_fails(self):
        """Tests that the sequence of a 'slave' factory cannot be reset."""
        class SubTestObjectFactory(self.TestObjectFactory):
            pass

        with self.assertRaises(ValueError):
            SubTestObjectFactory.reset_sequence()

    def test_reset_sequence_subclass_force(self):
        """Tests that reset_sequence(force=True) works."""
        class SubTestObjectFactory(self.TestObjectFactory):
            pass

        o1 = SubTestObjectFactory()
        self.assertEqual(0, o1.one)

        o2 = SubTestObjectFactory()
        self.assertEqual(1, o2.one)

        SubTestObjectFactory.reset_sequence(force=True)
        o3 = SubTestObjectFactory()
        self.assertEqual(0, o3.one)

        # The master sequence counter has been reset
        o4 = self.TestObjectFactory()
        self.assertEqual(1, o4.one)

    def test_reset_sequence_subclass_parent(self):
        """Tests that the sequence of a 'slave' factory cannot be reset."""
        class SubTestObjectFactory(self.TestObjectFactory):
            pass

        o1 = SubTestObjectFactory()
        self.assertEqual(0, o1.one)

        o2 = SubTestObjectFactory()
        self.assertEqual(1, o2.one)

        self.TestObjectFactory.reset_sequence()
        o3 = SubTestObjectFactory()
        self.assertEqual(0, o3.one)

        o4 = self.TestObjectFactory()
        self.assertEqual(1, o4.one)


class FactoryDefaultStrategyTestCase(unittest.TestCase):
    def test_build_strategy(self):
        class TestModelFactory(base.Factory):
            class Meta:
                model = TestModel
                strategy = enums.BUILD_STRATEGY

            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(test_model.id)

    def test_create_strategy(self):
        # Default Meta.strategy

        class TestModelFactory(FakeModelFactory):
            class Meta:
                model = TestModel

            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def test_stub_strategy(self):
        class TestModelFactory(base.Factory):
            class Meta:
                model = TestModel
                strategy = enums.STUB_STRATEGY

            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(hasattr(test_model, 'id'))  # We should have a plain old object

    def test_unknown_strategy(self):
        class TestModelFactory(base.Factory):
            class Meta:
                model = TestModel
                strategy = 'unknown'

            one = 'one'

        with self.assertRaises(base.Factory.UnknownStrategy):
            TestModelFactory()

    def test_stub_with_create_strategy(self):
        class TestModelFactory(base.StubFactory):
            class Meta:
                model = TestModel
                strategy = enums.CREATE_STRATEGY

            one = 'one'

        with self.assertRaises(base.StubFactory.UnsupportedStrategy):
            TestModelFactory()

    def test_stub_with_build_strategy(self):
        class TestModelFactory(base.StubFactory):
            class Meta:
                model = TestModel
                strategy = enums.BUILD_STRATEGY

            one = 'one'

        obj = TestModelFactory()

        # For stubs, build() is an alias of stub().
        self.assertFalse(isinstance(obj, TestModel))

    def test_change_strategy(self):
        class TestModelFactory(base.StubFactory):
            class Meta:
                model = TestModel
                strategy = enums.CREATE_STRATEGY

            one = 'one'

        self.assertEqual(enums.CREATE_STRATEGY, TestModelFactory._meta.strategy)


class DictFactoryTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        pet_sequence_offset = 10

        class Pet(base.DictFactory):
            @classmethod
            def _setup_next_sequence(cls) -> int:
                return pet_sequence_offset

            pet_id = declarations.Sequence(lambda n: n)

        class Cat(Pet):
            pass

        class Dog(Pet):
            pass

        self.Pet = Pet
        self.Cat = Cat
        self.Dog = Dog
        self.pet_sequence_offset = pet_sequence_offset

    def test_override_setup_next_sequence(self):
        result = self.Pet()
        self.assertEqual(result['pet_id'], self.pet_sequence_offset)

    def test_descendants_share_counter(self):
        cat_result = self.Cat()
        dog_result = self.Dog()
        results = [cat_result['pet_id'], dog_result['pet_id']]
        self.assertEqual(results, [self.pet_sequence_offset, self.pet_sequence_offset + 1])


class FactoryCreationTestCase(unittest.TestCase):
    def test_factory_for(self):
        class TestFactory(base.Factory):
            class Meta:
                model = TestObject

        self.assertTrue(isinstance(TestFactory.build(), TestObject))

    def test_stub(self):
        class TestFactory(base.StubFactory):
            pass

        self.assertEqual(TestFactory._meta.strategy, enums.STUB_STRATEGY)

    def test_inheritance_with_stub(self):
        class TestObjectFactory(base.StubFactory):
            class Meta:
                model = TestObject

            pass

        class TestFactory(TestObjectFactory):
            pass

        self.assertEqual(TestFactory._meta.strategy, enums.STUB_STRATEGY)

    def test_stub_and_subfactory(self):
        class StubA(base.StubFactory):
            class Meta:
                model = TestObject

            one = 'blah'

        class StubB(base.StubFactory):
            class Meta:
                model = TestObject

            stubbed = declarations.SubFactory(StubA, two='two')

        b = StubB()
        self.assertEqual('blah', b.stubbed.one)
        self.assertEqual('two', b.stubbed.two)

    def test_custom_creation(self):
        class TestModelFactory(FakeModelFactory):
            class Meta:
                model = TestModel

            @classmethod
            def _generate(cls, create, attrs):
                attrs['four'] = 4
                return super()._generate(create, attrs)

        b = TestModelFactory.build(one=1)
        self.assertEqual(1, b.one)
        self.assertEqual(4, b.four)
        self.assertEqual(None, b.id)

        c = TestModelFactory(one=1)
        self.assertEqual(1, c.one)
        self.assertEqual(4, c.four)
        self.assertEqual(1, c.id)

    # Errors

    def test_no_associated_class(self):
        class Test(base.Factory):
            pass

        self.assertTrue(Test._meta.abstract)


class PostGenerationParsingTestCase(unittest.TestCase):

    def test_extraction(self):
        class TestObjectFactory(base.Factory):
            class Meta:
                model = TestObject

            foo = declarations.PostGenerationDeclaration()

        self.assertIn('foo', TestObjectFactory._meta.post_declarations.as_dict())

    def test_classlevel_extraction(self):
        class TestObjectFactory(base.Factory):
            class Meta:
                model = TestObject

            foo = declarations.PostGenerationDeclaration()
            foo__bar = 42

        self.assertIn('foo', TestObjectFactory._meta.post_declarations.as_dict())
        self.assertIn('foo__bar', TestObjectFactory._meta.post_declarations.as_dict())
