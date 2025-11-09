from typing import TypeVar

from reactivex import Observable, abc, empty
from reactivex.internal import ArgumentOutOfRangeException, curry_flip

_T = TypeVar("_T")


@curry_flip
def take_(source: Observable[_T], count: int) -> Observable[_T]:
    """Returns a specified number of contiguous elements from the start of
    an observable sequence.

    Example:
        >>> result = source.pipe(take(5))
        >>> result = take(5)(source)

    Args:
        source: The source observable sequence.
        count: The number of elements to return.

    Returns:
        An observable sequence that contains the specified number of
        elements from the start of the input sequence.

    Raises:
        ArgumentOutOfRangeException: If count is negative.
    """
    if count < 0:
        raise ArgumentOutOfRangeException()

    if not count:
        return empty()

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
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
