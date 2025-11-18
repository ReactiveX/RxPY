from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip
from reactivex.notification import Notification, OnCompleted, OnError, OnNext

_T = TypeVar("_T")


@curry_flip
def materialize_(source: Observable[_T]) -> Observable[Notification[_T]]:
    """Materializes the implicit notifications of an observable
    sequence as explicit notification values.

    Examples:
        >>> res = source.pipe(materialize())
        >>> res = materialize()(source)

    Args:
        source: Source observable to materialize.

    Returns:
        An observable sequence containing the materialized
        notification values from the source sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[Notification[_T]],
        scheduler: abc.SchedulerBase | None = None,
    ):
        def on_next(value: _T) -> None:
            observer.on_next(OnNext(value))

        def on_error(error: Exception) -> None:
            observer.on_next(OnError(error))
            observer.on_completed()

        def on_completed() -> None:
            observer.on_next(OnCompleted())
            observer.on_completed()

        return source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)

    return Observable(subscribe)


__all__ = ["materialize_"]
