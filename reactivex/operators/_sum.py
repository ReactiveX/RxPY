from typing import Any

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.typing import Mapper


@curry_flip
def sum_(
    source: Observable[Any],
    key_mapper: Mapper[Any, float] | None = None,
) -> Observable[float]:
    """Computes the sum of a sequence of values.

    Examples:
        >>> result = source.pipe(sum())
        >>> result = sum()(source)
        >>> result = source.pipe(sum(lambda x: x.value))

    Args:
        source: The source observable.
        key_mapper: Optional mapper to extract numeric values.

    Returns:
        An observable sequence containing a single element with the sum.
    """
    if key_mapper:
        return source.pipe(ops.map(key_mapper), ops.sum())

    def accumulator(prev: float, cur: float) -> float:
        return prev + cur

    return source.pipe(ops.reduce(seed=0, accumulator=accumulator))


__all__ = ["sum_"]
