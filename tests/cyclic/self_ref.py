# Copyright: See the LICENSE file.

"""Helper to test circular factory dependencies."""

import factory


class TreeElement:
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name


class TreeElementFactory(factory.Factory):
    class Meta:
        model = TreeElement

    name = factory.Sequence(lambda n: "tree%s" % n)
    parent = factory.SubFactory('tests.cyclic.self_ref.TreeElementFactory')


class TreeElementRelatedFactory(factory.Factory):
    class Meta:
        model = TreeElement

    name = factory.Sequence(lambda n: "tree%s" % n)
    parent = factory.RelatedFactory('tests.cyclic.self_ref.TreeElementFactory')


class TreeElementTraitFactory(factory.Factory):
    class Meta:
        model = TreeElement

    name = factory.Sequence(lambda n: "tree%s" % n)
    parent = None

    class Params:
        with_parent = factory.Trait(
            parent=factory.SubFactory(
                'tests.cyclic.self_ref.TreeElementFactory', parent=None
            )
        )


class TreeElementTraitRelatedFactory(factory.Factory):
    class Meta:
        model = TreeElement

    name = factory.Sequence(lambda n: "tree%s" % n)
    parent = None

    class Params:
        with_parent = factory.Trait(
            parent=factory.RelatedFactory(
                'tests.cyclic.self_ref.TreeElementFactory', parent=None
            )
        )
