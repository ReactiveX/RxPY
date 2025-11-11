from typing import TypeVar

from reactivex import Observable, abc
from reactivex import operators as ops
from reactivex.internal import curry_flip
from reactivex.typing import Predicate

_T = TypeVar("_T")


@curry_flip
def some_(
    source: Observable[_T],
    predicate: Predicate[_T] | None = None,
) -> Observable[bool]:
    """Determines whether some element of an observable sequence satisfies a
    condition if present, else if some items are in the sequence.

    Examples:
        >>> res = source.pipe(some())
        >>> res = some()(source)
        >>> res = source.pipe(some(lambda x: x > 3))

    Args:
        source: The source observable sequence.
        predicate: A function to test each element for a condition.

    Returns:
        An observable sequence containing a single element
        determining whether some elements in the source sequence
        pass the test in the specified predicate if given, else if
        some items are in the sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[bool],
        scheduler: abc.SchedulerBase | None = None,
    ):
        def on_next(_: _T):
            observer.on_next(True)
            observer.on_completed()

        def on_error():
            observer.on_next(False)
            observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, on_error, scheduler=scheduler
        )

    if predicate:
        return source.pipe(
            ops.filter(predicate),
            ops.some(),
        )

    return Observable(subscribe)


__all__ = ["some_"]
