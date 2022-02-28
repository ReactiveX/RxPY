from typing import Callable, Optional, Set, TypeVar

from reactivex import Observable, abc

_T = TypeVar("_T")


def to_set_() -> Callable[[Observable[_T]], Observable[Set[_T]]]:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    def to_set(source: Observable[_T]) -> Observable[Set[_T]]:
        def subscribe(
            observer: abc.ObserverBase[Set[_T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            s: Set[_T] = set()

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
