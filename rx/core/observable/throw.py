from rx.core import Observable, AnonymousObservable

from rx.concurrency import immediate_scheduler


def throw(exception: Exception) -> Observable:
    """Returns an observable sequence that terminates with an exception,
    using the specified scheduler to send out the single OnError
    message.

    Example:
        >>> res = rx.Observable.throw(Exception('Error'))

    Args:
        exception -- An object used for the sequence's termination.

    Returns:
        The observable sequence that terminates exceptionally with the
        specified exception object.
    """

    exception = exception if isinstance(exception, Exception) else Exception(exception)

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or immediate_scheduler

        def action(scheduler, state):
            observer.on_error(exception)

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)
