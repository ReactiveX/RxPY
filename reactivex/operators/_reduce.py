from typing import Any, Callable, Type, TypeVar, Union, cast

from reactivex import Observable, compose
from reactivex import operators as ops
from reactivex.internal.utils import NotSet
from reactivex.typing import Accumulator

_T = TypeVar("_T")
_TState = TypeVar("_TState")


def reduce_(
    accumulator: Accumulator[_TState, _T], seed: Union[_TState, Type[NotSet]] = NotSet
) -> Callable[[Observable[_T]], Observable[Any]]:
    """Applies an accumulator function over an observable sequence,
    returning the result of the aggregation as a single element in the
    result sequence. The specified seed value is used as the initial
    accumulator value.

    For aggregation behavior with incremental intermediate results, see
    `scan()`.

    Examples:
        >>> res = reduce(lambda acc, x: acc + x)
        >>> res = reduce(lambda acc, x: acc + x, 0)

    Args:
        accumulator: An accumulator function to be
            invoked on each element.
        seed: Optional initial accumulator value.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with the
        final accumulator value.
    """
    if seed is not NotSet:
        seed_: _TState = cast(_TState, seed)
        scanner = ops.scan(accumulator, seed=seed_)
        return compose(
            scanner,
            ops.last_or_default(default_value=seed_),
        )

    return compose(
        ops.scan(cast(Accumulator[_T, _T], accumulator)),
        ops.last(),
    )


__all__ = ["reduce_"]
