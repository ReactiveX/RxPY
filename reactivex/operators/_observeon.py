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

    Note that this does not process items in parallel. Notifications
    are delivered one at a time, so this changes which thread the
    callbacks run on, not how many of them run at once. To parallelize
    the items of a sequence, give each item its own subscription with
    flat_map and merge the results, for example::

        source.pipe(
            ops.flat_map(
                lambda value: reactivex.just(value).pipe(
                    ops.subscribe_on(scheduler),
                    ops.map(long_running_function),
                )
            )
        )

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
