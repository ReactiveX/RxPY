from typing import Callable, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Mapper

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def _sum(key_mapper: Optional[Mapper[_T1, _T2]] = None) -> Callable[[Observable[_T1]], Observable[_T2]]:
    if key_mapper:
        return pipe(ops.map(key_mapper), ops.sum())

    return ops.reduce(seed=0, accumulator=lambda prev, curr: prev + curr)


__all__ = ["_sum"]
