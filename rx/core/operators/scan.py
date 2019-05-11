from typing import Any, Callable

from rx import defer, operators as ops
from rx.internal.utils import NotSet
from rx.core import Observable


def _scan(accumulator: Callable[[Any, Any], Any], seed: Any = NotSet) -> Callable[[Observable], Observable]:
    has_seed = seed is not NotSet

    def scan(source: Observable) -> Observable:
        """Partially applied scan operator.

        Applies an accumulator function over an observable sequence and
        returns each intermediate result.

        Examples:
            >>> scanned = scan(source)

        Args:
            source: The observable source to scan.

        Returns:
            An observable sequence containing the accumulated values.
        """

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
            return source.pipe(ops.map(projection))
        return defer(factory)
    return scan
