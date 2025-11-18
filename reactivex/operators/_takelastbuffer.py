from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def take_last_buffer_(source: Observable[_T], count: int) -> Observable[list[_T]]:
    """Returns an array with the specified number of contiguous
    elements from the end of an observable sequence.

    Example:
        >>> res = source.pipe(take_last_buffer(5))
        >>> res = take_last_buffer(5)(source)

    This operator accumulates a buffer with a length enough to
    store elements count elements. Upon completion of the source
    sequence, this buffer is drained on the result sequence. This
    causes the elements to be delayed.

    Args:
        source: Source observable to take elements from.
        count: Number of elements to take from the end.

    Returns:
        An observable sequence containing a single list with the
        specified number of elements from the end of the source
        sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[list[_T]],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        q: list[_T] = []

        def on_next(x: _T) -> None:
            with source.lock:
                q.append(x)
                if len(q) > count:
                    q.pop(0)

        def on_completed() -> None:
            observer.on_next(q)
            observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["take_last_buffer_"]
