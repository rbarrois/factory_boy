# Copyright: See the LICENSE file.


"""factory_boy extensions for use with the mogo library (pymongo wrapper)."""
from typing import TypeVar

from . import base

T = TypeVar("T")


class MogoFactory(base.Factory[T]):
    """Factory for mogo objects."""
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        return model_class(*args, **kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = model_class(*args, **kwargs)
        instance.save()
        return instance
