from typing import Callable, Type, TypeVar, Union, cast

from reactivex import Observable, abc, defer
from reactivex import operators as ops
from reactivex.internal.utils import NotSet
from reactivex.typing import Accumulator

_T = TypeVar("_T")
_TState = TypeVar("_TState")


def scan_(
    accumulator: Accumulator[_TState, _T], seed: Union[_TState, Type[NotSet]] = NotSet
) -> Callable[[Observable[_T]], Observable[_TState]]:
    has_seed = seed is not NotSet

    def scan(source: Observable[_T]) -> Observable[_TState]:
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

        def factory(scheduler: abc.SchedulerBase) -> Observable[_TState]:
            has_accumulation = False
            accumulation: _TState = cast(_TState, None)

            def projection(x: _T) -> _TState:
                nonlocal has_accumulation
                nonlocal accumulation

                if has_accumulation:
                    accumulation = accumulator(accumulation, x)
                else:
                    accumulation = (
                        accumulator(cast(_TState, seed), x)
                        if has_seed
                        else cast(_TState, x)
                    )
                    has_accumulation = True

                return accumulation

            return source.pipe(ops.map(projection))

        return defer(factory)

    return scan


__all__ = ["scan_"]
