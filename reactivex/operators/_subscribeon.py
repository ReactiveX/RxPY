from typing import Any, Callable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.disposable import (
    ScheduledDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)

_T = TypeVar("_T")


def subscribe_on_(
    scheduler: abc.SchedulerBase,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def subscribe_on(source: Observable[_T]) -> Observable[_T]:
        """Subscribe on the specified scheduler.

        Wrap the source sequence in order to run its subscription and
        unsubscription logic on the specified scheduler. This operation
        is not commonly used; see the remarks section for more
        information on the distinction between subscribe_on and
        observe_on.

        This only performs the side-effects of subscription and
        unsubscription on the specified scheduler. In order to invoke
        observer callbacks on a scheduler, use observe_on.

        Args:
            source: The source observable..

        Returns:
            The source sequence whose subscriptions and
            un-subscriptions happen on the specified scheduler.
        """

        def subscribe(
            observer: abc.ObserverBase[_T], _: Optional[abc.SchedulerBase] = None
        ):
            m = SingleAssignmentDisposable()
            d = SerialDisposable()
            d.disposable = m

            def action(scheduler: abc.SchedulerBase, state: Optional[Any] = None):
                d.disposable = ScheduledDisposable(
                    scheduler, source.subscribe(observer)
                )

            m.disposable = scheduler.schedule(action)
            return d

        return Observable(subscribe)

    return subscribe_on


__all__ = ["subscribe_on_"]
