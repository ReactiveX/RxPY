from rx.core import Observable, ObservableBase


def start(func, scheduler=None) -> ObservableBase:
    """Invokes the specified function asynchronously on the specified
    scheduler, surfacing the result through an observable sequence.

    Example:
    res = rx.Observable.start(lambda: pprint('hello'))
    res = rx.Observable.start(lambda: pprint('hello'), rx.Scheduler.timeout)

    Keyword arguments:
    func -- Function to run asynchronously.
    scheduler -- [Optional] Scheduler to run the function on. If
        not specified, defaults to Scheduler.timeout.

    Returns an observable sequence exposing the function's result value,
    or an exception.

    Remarks:
    The function is called immediately, not during the subscription of
    the resulting sequence. Multiple subscriptions to the resulting
    sequence can observe the function's result.
    """

    return Observable.to_async(func, scheduler)()
