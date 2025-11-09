from typing import TypeVar, cast

from reactivex import Observable, abc, defer
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.internal.utils import NotSet
from reactivex.typing import Accumulator

_T = TypeVar("_T")
_TState = TypeVar("_TState")


@curry_flip
def scan_(
    source: Observable[_T],
    accumulator: Accumulator[_TState, _T],
    seed: _TState | type[NotSet] = NotSet,
) -> Observable[_TState]:
    """Applies an accumulator function over an observable sequence and
    returns each intermediate result.

    Examples:
        >>> result = source.pipe(scan(lambda acc, x: acc + x, 0))
        >>> result = scan(lambda acc, x: acc + x, 0)(source)
        >>> result = source.pipe(scan(lambda acc, x: acc + x))

    Args:
        source: The observable source to scan.
        accumulator: An accumulator function to invoke on each element.
        seed: Optional initial accumulator value.

    Returns:
        An observable sequence containing the accumulated values.
    """
    has_seed = seed is not NotSet

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


__all__ = ["scan_"]
