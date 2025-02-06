# Copyright: See the LICENSE file.

import importlib.metadata

from . import alchemy, django, mogo, mongoengine
from .base import (
    BaseDictFactory,
    BaseListFactory,
    DictFactory,
    Factory,
    ListFactory,
    StubFactory,
    use_strategy,
)
from .declarations import (
    ContainerAttribute,
    Dict,
    Iterator,
    LazyAttribute,
    LazyAttributeSequence,
    LazyFunction,
    List,
    Maybe,
    PostGeneration,
    PostGenerationMethodCall,
    RelatedFactory,
    RelatedFactoryList,
    SelfAttribute,
    Sequence,
    SubFactory,
    Trait,
    Transformer,
)
from .enums import BUILD_STRATEGY, CREATE_STRATEGY, STUB_STRATEGY
from .errors import FactoryError
from .faker import Faker
from .helpers import (
    build,
    build_batch,
    container_attribute,
    create,
    create_batch,
    debug,
    generate,
    generate_batch,
    iterator,
    lazy_attribute,
    lazy_attribute_sequence,
    make_factory,
    post_generation,
    sequence,
    simple_generate,
    simple_generate_batch,
    stub,
    stub_batch,
)

__author__ = 'Raphaël Barrois <raphael.barrois+fboy@polytechnique.org>'
__version__ = importlib.metadata.version("factory_boy")
