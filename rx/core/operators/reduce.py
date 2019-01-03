from typing import Any, Callable
from rx.core import Observable

from rx import operators as _


def reduce(accumulator: Callable[[Any, Any], Any], seed: Any = None) -> Callable[[Observable], Observable]:
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

    scanner = _.scan(accumulator, seed=seed)
    initial = _.start_with(seed)

    def partial(source: Observable) -> Observable:
        if seed is not None:
            return source.pipe(scanner, initial, _.last())
        else:
            return source.pipe(_.scan(accumulator), _.last())
    return partial
