from typing import Any, Callable

from rx import defer, operators as ops
from rx.internal.utils import NotSet
from rx.core import Observable
from rx.core.typing import Accumulator

def _scan(accumulator: Accumulator, seed: Any = NotSet) -> Callable[[Observable], Observable]:
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
            has_accumulation = False
            accumulation = None

            def projection(x):
                nonlocal has_accumulation
                nonlocal accumulation

                if has_accumulation:
                    accumulation = accumulator(accumulation, x)
                else:
                    accumulation = accumulator(seed, x) if has_seed else x
                    has_accumulation = True

                return accumulation
            return source.pipe(ops.map(projection))
        return defer(factory)
    return scan
