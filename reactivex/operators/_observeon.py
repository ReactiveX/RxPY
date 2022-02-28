from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.observer import ObserveOnObserver

_T = TypeVar("_T")


def observe_on_(
    scheduler: abc.SchedulerBase,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def observe_on(source: Observable[_T]) -> Observable[_T]:
        """Wraps the source sequence in order to run its observer
        callbacks on the specified scheduler.

        This only invokes observer callbacks on a scheduler. In case
        the subscription and/or unsubscription actions have
        side-effects that require to be run on a scheduler, use
        subscribe_on.

        Args:
            source: Source observable.


        Returns:
            Returns the source sequence whose observations happen on
            the specified scheduler.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            subscribe_scheduler: Optional[abc.SchedulerBase] = None,
        ):
            return source.subscribe(
                ObserveOnObserver(scheduler, observer), scheduler=subscribe_scheduler
            )

        return Observable(subscribe)

    return observe_on


__all__ = ["observe_on_"]
