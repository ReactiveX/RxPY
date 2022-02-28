from typing import Callable, Optional, TypeVar

from reactivex import Notification, Observable, abc

_T = TypeVar("_T")


def dematerialize_() -> Callable[[Observable[Notification[_T]]], Observable[_T]]:
    def dematerialize(source: Observable[Notification[_T]]) -> Observable[_T]:
        """Partially applied dematerialize operator.

        Dematerializes the explicit notification values of an
        observable sequence as implicit notifications.

        Returns:
            An observable sequence exhibiting the behavior
            corresponding to the source sequence's notification values.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            def on_next(value: Notification[_T]) -> None:
                return value.accept(observer)

            return source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return dematerialize


__all__ = ["dematerialize_"]
