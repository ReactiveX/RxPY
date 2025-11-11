from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def take_last_(source: Observable[_T], count: int) -> Observable[_T]:
    """Returns a specified number of contiguous elements from the end of an
    observable sequence.

    Examples:
        >>> res = source.pipe(take_last(5))
        >>> res = take_last(5)(source)

    This operator accumulates a buffer with a length enough to store
    elements count elements. Upon completion of the source sequence, this
    buffer is drained on the result sequence. This causes the elements to be
    delayed.

    Args:
        source: The source observable sequence.
        count: Number of elements to take from the end of the source
            sequence.

    Returns:
        An observable sequence containing the specified number of elements
        from the end of the source sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        q: list[_T] = []

        def on_next(x: _T) -> None:
            q.append(x)
            if len(q) > count:
                q.pop(0)

        def on_completed():
            while q:
                observer.on_next(q.pop(0))
            observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["take_last_"]
