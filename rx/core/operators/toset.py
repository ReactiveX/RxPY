from typing import Callable, TypeVar, Set, Optional

from rx.core import Observable, abc

_T = TypeVar("_T")


def _to_set() -> Callable[[Observable[_T]], Observable[Set[_T]]]:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    def to_set(source: Observable[_T]) -> Observable[Set[_T]]:
        def subscribe(
            observer: abc.ObserverBase[Set[_T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            s = set[_T]()

            def on_completed() -> None:
                nonlocal s
                observer.on_next(s)
                s = set[_T]()
                observer.on_completed()

            return source.subscribe_(s.add, observer.on_error, on_completed, scheduler)

        return Observable(subscribe)

    return to_set


__all__ = ["_to_set"]
