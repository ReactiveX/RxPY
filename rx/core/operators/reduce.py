from typing import Any, Callable
from rx.core import Observable, pipe

from rx import operators


def reduce(accumulator: Callable[[Any, Any], Any], seed: Any = None) -> Observable:
    """Applies an accumulator function over an observable sequence,
    returning the result of the aggregation as a single element in the
    result sequence. The specified seed value is used as the initial
    accumulator value.

    For aggregation behavior with incremental intermediate results, see
    Observable.scan.

    Examples:
        >>> res = reduce(lambda acc, x: acc + x)
        >>> res = reduce(lambda acc, x: acc + x, 0)

    Keyword arguments:
        accumulator -- An accumulator function to be
            invoked on each element.
        seed -- Optional initial accumulator value.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with the
        final accumulator value.
    """

    scanner = operators.scan(accumulator, seed=seed)
    initial = operators.start_with(seed)

    def partial(source: Observable) -> Observable:
        if seed is not None:
            return pipe(scanner, initial, operators.last())
        else:
            return pipe(scan(accumulator), operators.last())
    return partial