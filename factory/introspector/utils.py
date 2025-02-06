import factory


def enum_declaration(enum_class):
    return factory.Faker(
        "random_choices",
        elements=[member for member, _ in enum_class.field.__class__.__members__.items()]
    )


def none_declaration():
    return factory.Faker(
        "random_choices",
        elements=[None]
    )
