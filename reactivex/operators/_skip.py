from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import ArgumentOutOfRangeException, curry_flip

_T = TypeVar("_T")


@curry_flip
def skip_(source: Observable[_T], count: int) -> Observable[_T]:
    """Bypasses a specified number of elements in an observable sequence
    and then returns the remaining elements.

    Examples:
        >>> result = source.pipe(skip(5))
        >>> result = skip(5)(source)

    Args:
        source: The source observable.
        count: The number of elements to skip.

    Returns:
        An observable sequence that contains the elements that occur
        after the specified index in the input sequence.

    Raises:
        ArgumentOutOfRangeException: If count is negative.
    """
    if count < 0:
        raise ArgumentOutOfRangeException()

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        remaining = count

        def on_next(value: _T) -> None:
            nonlocal remaining

            if remaining <= 0:
                observer.on_next(value)
            else:
                remaining -= 1

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["skip_"]
