from typing import Any, Callable
from rx import defer
from rx.core import Observable


def scan(accumulator: Callable[[Any, Any], Any], seed: Any = None) -> Callable[[Observable], Observable]:
    """Applies an accumulator function over an observable sequence and
    returns each intermediate result. The optional seed value is used as
    the initial accumulator value. For aggregation behavior with no
    intermediate results, see `aggregate()` or `Observable()`.

    Examples:
        >>> scanned = source.scan(lambda acc, x: acc + x)
        >>> scanned = source.scan(lambda acc, x: acc + x, 0)

    Args:
        accumulator: An accumulator function to be invoked on each
            element.
        seed: [Optional] The initial accumulator value.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing the accumulated values.
    """

    has_seed = seed is not None

    def partial(source: Observable) -> Observable:
        def factory(scheduler):
            nonlocal source

            has_accumulation = [False]
            accumulation = [None]

            def projection(x):
                if has_accumulation[0]:
                    accumulation[0] = accumulator(accumulation[0], x)
                else:
                    accumulation[0] = accumulator(seed, x) if has_seed else x
                    has_accumulation[0] = True

                return accumulation[0]
            return source.map(projection)
        return defer(factory)
    return partial
