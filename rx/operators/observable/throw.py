from rx.core import Observable, AnonymousObservable

from rx.concurrency import immediate_scheduler
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable, alias="throw_exception")
def throw(cls, exception):
    """Returns an observable sequence that terminates with an exception,
    using the specified scheduler to send out the single OnError message.

    1 - res = rx.Observable.throw_exception(Exception('Error'))

    Keyword arguments:
    exception -- An object used for the sequence's termination.

    Returns the observable sequence that terminates exceptionally with the
    specified exception object.
    """

    exception = exception if isinstance(exception, Exception) else Exception(exception)

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or immediate_scheduler

        def action(scheduler, state):
            observer.throw(exception)

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)
