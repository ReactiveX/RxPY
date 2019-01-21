from typing import Callable

from rx.core import AnonymousObservable, Observable
from rx.core.observer import ObserveOnObserver


def _observe_on(scheduler) -> Callable[[Observable], Observable]:
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
        def subscribe(observer, _=None):
            return source.subscribe(ObserveOnObserver(scheduler, observer))

        return AnonymousObservable(subscribe)
    return observe_on