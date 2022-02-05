from typing import Callable, TypeVar

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Predicate

_T = TypeVar("_T")


def all(predicate: Predicate[_T]) -> Callable[[Observable[_T]], Observable[bool]]:

    filtering = ops.filter(lambda v: not predicate(v))
    mapping = ops.map(lambda b: not b)
    some = ops.some()

    return pipe(filtering, some, mapping)


__all__ = ["all"]
