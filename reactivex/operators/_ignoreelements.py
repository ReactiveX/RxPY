from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.internal import noop

_T = TypeVar("_T")


def ignore_elements_() -> Callable[[Observable[_T]], Observable[_T]]:
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    Returns:
        An empty observable {Observable} sequence that signals
        termination, successful or exceptional, of the source sequence.
    """

    def ignore_elements(source: Observable[_T]) -> Observable[_T]:
        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            return source.subscribe(
                noop, observer.on_error, observer.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return ignore_elements


__all__ = ["ignore_elements_"]
