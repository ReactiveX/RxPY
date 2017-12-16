from typing import Any, Callable
from rx.core import Observable


def reduce(source: Observable, accumulator: Callable[[Any, Any], Any], seed: Any=None) -> Observable:
    """Applies an accumulator function over an observable sequence,
    returning the result of the aggregation as a single element in the
    result sequence. The specified seed value is used as the initial
    accumulator value.

    For aggregation behavior with incremental intermediate results, see
    Observable.scan.

    Example:
    1 - res = source.reduce(lambda acc, x: acc + x)
    2 - res = source.reduce(lambda acc, x: acc + x, 0)

    Keyword arguments:
    :param types.FunctionType accumulator: An accumulator function to be
        invoked on each element.
    :param T seed: Optional initial accumulator value.

    :returns: An observable sequence containing a single element with the
        final accumulator value.
    :rtype: Observable
    """

    if seed is not None:
        return source.scan(accumulator, seed=seed).start_with(seed).last()
    else:
        return source.scan(accumulator).last()
