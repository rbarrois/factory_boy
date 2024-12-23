import decimal
import random

import faker.generator

randgen = random.Random()

randgen.state_set = False


def get_random_state():
    """Retrieve the state of factory.fuzzy's random generator."""
    state = randgen.getstate()
    # Returned state must represent both Faker and factory_boy.
    faker.generator.random.setstate(state)
    return state


def set_random_state(state):
    """Force-set the state of factory.fuzzy's random generator."""
    randgen.state_set = True
    randgen.setstate(state)

    faker.generator.random.setstate(state)


def reseed_random(seed):
    """Reseed factory.fuzzy's random generator."""
    r = random.Random(seed)
    random_internal_state = r.getstate()
    set_random_state(random_internal_state)


def uniform_decimal(low, high):
    modifier = decimal.Decimal(randgen.random())
    return low + (high - low) * modifier
