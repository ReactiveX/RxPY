from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip
from reactivex.observer import ObserveOnObserver

_T = TypeVar("_T")


@curry_flip
def observe_on_(
    source: Observable[_T],
    scheduler: abc.SchedulerBase,
) -> Observable[_T]:
    """Wraps the source sequence in order to run its observer
    callbacks on the specified scheduler.

    This only invokes observer callbacks on a scheduler. In case
    the subscription and/or unsubscription actions have
    side-effects that require to be run on a scheduler, use
    subscribe_on.

    Examples:
        >>> res = source.pipe(observe_on(scheduler))
        >>> res = observe_on(scheduler)(source)

    Args:
        source: Source observable.
        scheduler: Scheduler to observe on.

    Returns:
        Returns the source sequence whose observations happen on
        the specified scheduler.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        subscribe_scheduler: abc.SchedulerBase | None = None,
    ):
        return source.subscribe(
            ObserveOnObserver(scheduler, observer), scheduler=subscribe_scheduler
        )

    return Observable(subscribe)


__all__ = ["observe_on_"]
