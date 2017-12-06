from rx.core import Observable, AnonymousObservable
from rx.concurrency import current_thread_scheduler


def return_value(value, scheduler=None) -> Observable:
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    example
    res = rx.Observable.return(42)
    res = rx.Observable.return(42, rx.Scheduler.timeout)

    Keyword arguments:
    value -- Single element in the resulting observable sequence.
    scheduler -- [Optional] Scheduler to send the single element on. If
        not specified, defaults to Scheduler.immediate.

    Returns an observable sequence containing the single specified
    element.
    """

    scheduler = scheduler or current_thread_scheduler

    def subscribe(observer):
        def action(scheduler, state=None):
            observer.on_next(value)
            observer.on_completed()

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)


def from_callable(supplier, scheduler=None) ->Observable:
    """Returns an observable sequence that contains a single element generate from a supplier,
       using the specified scheduler to send out observer messages.

       example
       res = rx.Observable.from_callable(lambda: calculate_value())
       res = rx.Observable.from_callable(lambda: 1 / 0) # emits an error

       Keyword arguments:
       value -- Single element in the resulting observable sequence.
       scheduler -- [Optional] Scheduler to send the single element on. If
           not specified, defaults to Scheduler.immediate.

       Returns an observable sequence containing the single specified
       element derived from the supplier
       """
    scheduler = scheduler or current_thread_scheduler

    def subscribe(observer):
        def action(scheduler, state=None):
            try:
                observer.on_next(supplier())
                observer.on_completed()
            except Exception as e:
                observer.on_error(e)
        return scheduler.schedule(action)

    return AnonymousObservable(subscribe)
