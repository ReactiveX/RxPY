from typing import Any, TypeVar

from reactivex import Observable, abc
from reactivex.disposable import (
    ScheduledDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def subscribe_on_(
    source: Observable[_T],
    scheduler: abc.SchedulerBase,
) -> Observable[_T]:
    """Subscribe on the specified scheduler.

    Wrap the source sequence in order to run its subscription and
    unsubscription logic on the specified scheduler. This operation
    is not commonly used; see the remarks section for more
    information on the distinction between subscribe_on and
    observe_on.

    This only performs the side-effects of subscription and
    unsubscription on the specified scheduler. In order to invoke
    observer callbacks on a scheduler, use observe_on.

    Examples:
        >>> res = source.pipe(subscribe_on(scheduler))
        >>> res = subscribe_on(scheduler)(source)

    Args:
        source: The source observable.
        scheduler: Scheduler to use for subscription/unsubscription.

    Returns:
        The source sequence whose subscriptions and
        un-subscriptions happen on the specified scheduler.
    """

    def subscribe(observer: abc.ObserverBase[_T], _: abc.SchedulerBase | None = None):
        m = SingleAssignmentDisposable()
        d = SerialDisposable()
        d.disposable = m

        def action(scheduler: abc.SchedulerBase, state: Any | None = None):
            d.disposable = ScheduledDisposable(
                scheduler, source.subscribe(observer, scheduler=scheduler)
            )

        m.disposable = scheduler.schedule(action)
        return d

    return Observable(subscribe)


__all__ = ["subscribe_on_"]
