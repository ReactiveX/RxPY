from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip, noop

_T = TypeVar("_T")


@curry_flip
def ignore_elements_(source: Observable[_T]) -> Observable[_T]:
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    Examples:
        >>> res = source.pipe(ignore_elements())
        >>> res = ignore_elements()(source)

    Args:
        source: The source observable sequence.

    Returns:
        An empty observable sequence that signals
        termination, successful or exceptional, of the source sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        return source.subscribe(
            noop, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["ignore_elements_"]
