from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.notification import Notification, OnCompleted, OnError, OnNext

_T = TypeVar("_T")


def materialize() -> Callable[[Observable[_T]], Observable[Notification[_T]]]:
    def materialize(source: Observable[_T]) -> Observable[Notification[_T]]:
        """Partially applied materialize operator.

        Materializes the implicit notifications of an observable
        sequence as explicit notification values.

        Args:
            source: Source observable to materialize.

        Returns:
            An observable sequence containing the materialized
            notification values from the source sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[Notification[_T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            def on_next(value: _T) -> None:
                observer.on_next(OnNext(value))

            def on_error(error: Exception) -> None:
                observer.on_next(OnError(error))
                observer.on_completed()

            def on_completed() -> None:
                observer.on_next(OnCompleted())
                observer.on_completed()

            return source.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return materialize


__all__ = ["materialize"]
