from typing import Optional, TypeVar, cast

from reactivex import Observable, abc, empty
from reactivex.curry import curry_flip
from reactivex.internal import ArgumentOutOfRangeException

_T = TypeVar("_T")


@curry_flip(1)
def take_(source: Observable[_T], count: int) -> Observable[_T]:
    if count < 0:
        raise ArgumentOutOfRangeException()

    """Returns a specified number of contiguous elements from the start of
    an observable sequence.

    >>> take(source)

    Keyword arguments:
    count -- The number of elements to return.

    Returns an observable sequence that contains the specified number of
    elements from the start of the input sequence.
    """

    if not count:
        return cast(Observable[_T], empty())

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: Optional[abc.SchedulerBase] = None,
    ):
        remaining = count

        def on_next(value: _T) -> None:
            nonlocal remaining

            if remaining > 0:
                remaining -= 1
                observer.on_next(value)
                if not remaining:
                    observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["take_"]
