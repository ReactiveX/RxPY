from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.internal import ArgumentOutOfRangeException

_T = TypeVar("_T")


def skip_(count: int) -> Callable[[Observable[_T]], Observable[_T]]:
    if count < 0:
        raise ArgumentOutOfRangeException()

    def skip(source: Observable[_T]) -> Observable[_T]:
        """The skip operator.

        Bypasses a specified number of elements in an observable sequence
        and then returns the remaining elements.

        Args:
            source: The source observable.

        Returns:
            An observable sequence that contains the elements that occur
            after the specified index in the input sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
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

    return skip


__all__ = ["skip_"]
