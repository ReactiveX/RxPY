from typing import Any, Callable

from rx import operators as ops
from rx.internal.utils import NotSet
from rx.core import Observable, pipe
from rx.core.typing import Accumulator


def _reduce(accumulator: Accumulator, seed: Any = NotSet) -> Callable[[Observable], Observable]:
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
        scanner = ops.scan(accumulator, seed=seed)
        return pipe(scanner, ops.last_or_default(default_value=seed))

    return pipe(ops.scan(accumulator), ops.last())
