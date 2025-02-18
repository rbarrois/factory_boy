# Copyright: See the LICENSE file.

import dataclasses
import unittest

from typing_extensions import assert_type

import factory


@dataclasses.dataclass
class User:
    name: str
    email: str
    id: int


class TypingTests(unittest.TestCase):
    def test_simple_factory(self) -> None:
        class UserFactory(factory.Factory[User]):
            name = "John Doe"
            email = "john.doe@example.org"
            id = 42

            class Meta:
                model = User

        assert_type(UserFactory.build(), User)
        assert_type(UserFactory.create(), User)
        assert_type(UserFactory.build_batch(2), list[User])
        assert_type(UserFactory.create_batch(2), list[User])
        self.assertEqual(UserFactory.create().name, "John Doe")

    def test_dict_factory(self) -> None:
        class Pet(factory.DictFactory):
            species = "dog"
            name = "rover"

        self.assertIsInstance(Pet.build(), dict)
        self.assertIsInstance(Pet.create(), dict)

    def test_list_factory(self) -> None:
        self.assertIsInstance(factory.ListFactory.build(), list)
        self.assertIsInstance(factory.ListFactory.create(), list)
