from typing import Callable, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Predicate

_T = TypeVar("_T")


def count_(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[int]]:

    if predicate:
        return pipe(
            ops.filter(predicate),
            ops.count(),
        )

    def reducer(n: int, _: _T) -> int:
        return n + 1

    counter = ops.reduce(reducer, seed=0)
    return counter


__all__ = ["count_"]
