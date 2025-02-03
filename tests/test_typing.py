# Copyright: See the LICENSE file.

import dataclasses
import unittest
from typing import List

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
        assert_type(UserFactory.build_batch(2), List[User])
        assert_type(UserFactory.create_batch(2), List[User])
        self.assertEqual(UserFactory.create().name, "John Doe")

    def test_dict_factory(self) -> None:

        class Pet(factory.DictFactory):
            species = "dog"
            name = "rover"

        assert_type(Pet.build(), dict)
        assert_type(Pet.create(), dict)

    def test_list_factory(self) -> None:
        assert_type(factory.ListFactory.build(), list)
        assert_type(factory.ListFactory.create(), list)
