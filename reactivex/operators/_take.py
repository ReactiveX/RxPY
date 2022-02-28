from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc, empty
from reactivex.internal import ArgumentOutOfRangeException

_T = TypeVar("_T")


def take_(count: int) -> Callable[[Observable[_T]], Observable[_T]]:
    if count < 0:
        raise ArgumentOutOfRangeException()

    def take(source: Observable[_T]) -> Observable[_T]:
        """Returns a specified number of contiguous elements from the start of
        an observable sequence.

        >>> take(source)

        Keyword arguments:
        count -- The number of elements to return.

        Returns an observable sequence that contains the specified number of
        elements from the start of the input sequence.
        """

        if not count:
            return empty()

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

    return take


__all__ = ["take_"]
