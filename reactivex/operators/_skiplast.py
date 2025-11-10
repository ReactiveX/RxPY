from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def skip_last_(source: Observable[_T], count: int) -> Observable[_T]:
    """Bypasses a specified number of elements at the end of an
    observable sequence.

    This operator accumulates a queue with a length enough to store
    the first `count` elements. As more elements are received,
    elements are taken from the front of the queue and produced on
    the result sequence. This causes elements to be delayed.

    Examples:
        >>> res = source.pipe(skip_last(5))
        >>> res = skip_last(5)(source)

    Args:
        source: Source observable.
        count: Number of elements to bypass at the end of the
        source sequence.

    Returns:
        An observable sequence containing the source sequence
        elements except for the bypassed ones at the end.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ):
        q: list[_T] = []

        def on_next(value: _T) -> None:
            front = None
            with source.lock:
                q.append(value)
                if len(q) > count:
                    front = q.pop(0)

            if front is not None:
                observer.on_next(front)

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["skip_last_"]
