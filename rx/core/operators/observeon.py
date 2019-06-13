from typing import Callable, Optional

from rx.core import Observable, typing
from rx.core.observer import ObserveOnObserver


def _observe_on(scheduler: typing.Scheduler) -> Callable[[Observable], Observable]:
    def observe_on(source: Observable) -> Observable:
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

        def subscribe_observer(observer: typing.Observer,
                               scheduler_: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            return source.subscribe_observer(ObserveOnObserver(scheduler, observer),
                                             scheduler=scheduler_)

        return Observable(subscribe_observer=subscribe_observer)
    return observe_on
