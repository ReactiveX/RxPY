from typing import Callable, Optional, Tuple, TypeVar

from reactivex import Observable, abc, compose
from reactivex import operators as ops
from reactivex import typing

_T = TypeVar("_T")


def skip_while_(
    predicate: typing.Predicate[_T],
) -> Callable[[Observable[_T]], Observable[_T]]:
    def skip_while(source: Observable[_T]) -> Observable[_T]:
        """Bypasses elements in an observable sequence as long as a
        specified condition is true and then returns the remaining
        elements. The element's index is used in the logic of the
        predicate function.

        Example:
            >>> skip_while(source)

        Args:
            source: The source observable to skip elements from.

        Returns:
            An observable sequence that contains the elements from the
            input sequence starting at the first element in the linear
            series that does not pass the test specified by predicate.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            running = False

            def on_next(value: _T):
                nonlocal running

                if not running:
                    try:
                        running = not predicate(value)
                    except Exception as exn:
                        observer.on_error(exn)
                        return

                if running:
                    observer.on_next(value)

            return source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return skip_while


def skip_while_indexed_(
    predicate: typing.PredicateIndexed[_T],
) -> Callable[[Observable[_T]], Observable[_T]]:
    def indexer(x: _T, i: int) -> Tuple[_T, int]:
        return (x, i)

    def skipper(x: Tuple[_T, int]) -> bool:
        return predicate(*x)

    def mapper(x: Tuple[_T, int]) -> _T:
        return x[0]

    return compose(
        ops.map_indexed(indexer),
        ops.skip_while(skipper),
        ops.map(mapper),
    )


__all__ = ["skip_while_", "skip_while_indexed_"]
