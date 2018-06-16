from rx.core import AnonymousObservable, ObservableBase
from rx.core.observeonobserver import ObserveOnObserver


def observe_on(source, scheduler) -> ObservableBase:
    """Wraps the source sequence in order to run its observer callbacks on
    the specified scheduler.

    Keyword arguments:
    scheduler -- Scheduler to notify observers on.

    Returns the source sequence whose observations happen on the specified
    scheduler.

    This only invokes observer callbacks on a scheduler. In case the
    subscription and/or unsubscription actions have side-effects
    that require to be run on a scheduler, use subscribe_on.
    """

    def subscribe(observer, scheduler=None):
        return source.subscribe(ObserveOnObserver(scheduler, observer))

    return AnonymousObservable(subscribe)
