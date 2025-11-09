from collections.abc import Callable
from typing import TypeVar

from reactivex import Observable, abc

_T = TypeVar("_T")


def to_set_() -> Callable[[Observable[_T]], Observable[set[_T]]]:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    def to_set(source: Observable[_T]) -> Observable[set[_T]]:
        def subscribe(
            observer: abc.ObserverBase[set[_T]],
            scheduler: abc.SchedulerBase | None = None,
        ) -> abc.DisposableBase:
            s: set[_T] = set()

            def on_completed() -> None:
                nonlocal s
                observer.on_next(s)
                s = set()
                observer.on_completed()

            return source.subscribe(
                s.add, observer.on_error, on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return to_set


__all__ = ["to_set_"]
