from typing import Any, TypeVar, cast

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.internal.utils import NotSet
from reactivex.typing import Accumulator

_T = TypeVar("_T")
_TState = TypeVar("_TState")


@curry_flip
def reduce_(
    source: Observable[_T],
    accumulator: Accumulator[_TState, _T],
    seed: _TState | type[NotSet] = NotSet,
) -> Observable[Any]:
    """Applies an accumulator function over an observable sequence,
    returning the result of the aggregation as a single element in the
    result sequence. The specified seed value is used as the initial
    accumulator value.

    For aggregation behavior with incremental intermediate results, see
    `scan()`.

    Examples:
        >>> result = source.pipe(reduce(lambda acc, x: acc + x))
        >>> result = reduce(lambda acc, x: acc + x)(source)
        >>> result = source.pipe(reduce(lambda acc, x: acc + x, 0))

    Args:
        source: The source observable.
        accumulator: An accumulator function to be invoked on each element.
        seed: Optional initial accumulator value.

    Returns:
        An observable sequence containing a single element with the
        final accumulator value.
    """
    if seed is not NotSet:
        seed_: _TState = cast(_TState, seed)
        scanner = ops.scan(accumulator, seed=seed_)
        return source.pipe(
            scanner,
            ops.last_or_default(default_value=seed_),
        )

    return source.pipe(
        ops.scan(cast(Accumulator[_T, _T], accumulator)),
        ops.last(),
    )


__all__ = ["reduce_"]
