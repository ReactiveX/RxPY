from typing import Callable, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Predicate

_T = TypeVar("_T")


def _count(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[int]]:

    if predicate:
        filtering = ops.filter(predicate)
        return pipe(filtering, ops.count())

    counter = ops.reduce(lambda n, _: n + 1, seed=0)
    return pipe(counter)


__all__ = ["_count"]
