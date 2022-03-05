from typing import Any, Callable, Optional

from reactivex import Observable, compose
from reactivex import operators as ops
from reactivex.typing import Mapper


def sum_(
    key_mapper: Optional[Mapper[Any, float]] = None
) -> Callable[[Observable[Any]], Observable[float]]:
    if key_mapper:
        return compose(ops.map(key_mapper), ops.sum())

    def accumulator(prev: float, cur: float) -> float:
        return prev + cur

    return ops.reduce(seed=0, accumulator=accumulator)


__all__ = ["sum_"]
