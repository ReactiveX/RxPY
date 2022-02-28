from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc

_T = TypeVar("_T")


def as_observable_() -> Callable[[Observable[_T]], Observable[_T]]:
    def as_observable(source: Observable[_T]) -> Observable[_T]:
        """Hides the identity of an observable sequence.

        Args:
            source: Observable source to hide identity from.

        Returns:
            An observable sequence that hides the identity of the
            source sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            return source.subscribe(observer, scheduler=scheduler)

        return Observable(subscribe)

    return as_observable


__all__ = ["as_observable_"]
