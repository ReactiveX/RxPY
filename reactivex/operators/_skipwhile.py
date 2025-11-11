from typing import TypeVar

from reactivex import Observable, abc, typing
from reactivex import operators as ops
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def skip_while_(
    source: Observable[_T],
    predicate: typing.Predicate[_T],
) -> Observable[_T]:
    """Bypasses elements in an observable sequence as long as a
    specified condition is true and then returns the remaining
    elements.

    Examples:
        >>> res = source.pipe(skip_while(lambda x: x < 3))
        >>> res = skip_while(lambda x: x < 3)(source)

    Args:
        source: The source observable to skip elements from.
        predicate: A function to test each element for a condition.

    Returns:
        An observable sequence that contains the elements from the
        input sequence starting at the first element in the linear
        series that does not pass the test specified by predicate.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
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


@curry_flip
def skip_while_indexed_(
    source: Observable[_T],
    predicate: typing.PredicateIndexed[_T],
) -> Observable[_T]:
    """Bypasses elements in an observable sequence as long as a
    specified condition is true and then returns the remaining
    elements. The element's index is used in the logic of the
    predicate function.

    Examples:
        >>> res = source.pipe(skip_while_indexed(lambda x, i: i < 3))
        >>> res = skip_while_indexed(lambda x, i: i < 3)(source)

    Args:
        source: The source observable to skip elements from.
        predicate: A function to test each element and its index for a condition.

    Returns:
        An observable sequence that contains the elements from the
        input sequence starting at the first element that does not
        pass the test specified by predicate.
    """

    def indexer(x: _T, i: int) -> tuple[_T, int]:
        return (x, i)

    def skipper(x: tuple[_T, int]) -> bool:
        return predicate(*x)

    def mapper(x: tuple[_T, int]) -> _T:
        return x[0]

    return source.pipe(
        ops.map_indexed(indexer),
        ops.skip_while(skipper),
        ops.map(mapper),
    )


__all__ = ["skip_while_", "skip_while_indexed_"]
