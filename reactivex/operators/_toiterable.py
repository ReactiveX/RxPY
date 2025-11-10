from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def to_iterable_(source: Observable[_T]) -> Observable[list[_T]]:
    """Creates an iterable from an observable sequence.

    Examples:
        >>> res = source.pipe(to_iterable())
        >>> res = to_iterable()(source)

    Args:
        source: Source observable.

    Returns:
        An observable sequence containing a single element with an
        iterable containing all the elements of the source
        sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[list[_T]],
        scheduler: abc.SchedulerBase | None = None,
    ):
        nonlocal source

        queue: list[_T] = []

        def on_next(item: _T):
            queue.append(item)

        def on_completed():
            nonlocal queue
            observer.on_next(queue)
            queue = []
            observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["to_iterable_"]
