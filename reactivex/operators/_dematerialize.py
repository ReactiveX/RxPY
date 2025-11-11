from typing import TypeVar

from reactivex import Notification, Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def dematerialize_(source: Observable[Notification[_T]]) -> Observable[_T]:
    """Dematerializes the explicit notification values of an
    observable sequence as implicit notifications.

    Examples:
        >>> res = source.pipe(dematerialize())
        >>> res = dematerialize()(source)

    Args:
        source: Source observable with notifications to dematerialize.

    Returns:
        An observable sequence exhibiting the behavior
        corresponding to the source sequence's notification values.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ):
        def on_next(value: Notification[_T]) -> None:
            return value.accept(observer)

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["dematerialize_"]
