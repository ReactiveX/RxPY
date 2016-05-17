from rx.core import Observable, AnonymousObservable, Disposable
from rx.disposables import SingleAssignmentDisposable, \
    CompositeDisposable, SerialDisposable
from rx.concurrency import immediate_scheduler
from rx.internal import Enumerable
from rx.internal import extensionmethod, extensionclassmethod


def catch_handler(source, handler):
    def subscribe(observer):
        d1 = SingleAssignmentDisposable()
        subscription = SerialDisposable()

        subscription.disposable = d1

        def on_error(exception):
            try:
                result = handler(exception)
            except Exception as ex:
                observer.on_error(ex)
                return

            result = Observable.from_future(result)
            d = SingleAssignmentDisposable()
            subscription.disposable = d
            d.disposable = result.subscribe(observer)

        d1.disposable = source.subscribe(
            observer.on_next,
            on_error,
            observer.on_completed
        )
        return subscription
    return AnonymousObservable(subscribe)


@extensionmethod(Observable, instancemethod=True)
def catch_exception(self, second=None, handler=None):
    """Continues an observable sequence that is terminated by an exception
    with the next observable sequence.

    1 - xs.catch_exception(ys)
    2 - xs.catch_exception(lambda ex: ys(ex))

    Keyword arguments:
    handler -- Exception handler function that returns an observable
        sequence  given the error that occurred in the first sequence.
    second -- Second observable sequence used to produce results when an
        error occurred in the first sequence.

    Returns an observable sequence containing the first sequence's
    elements, followed by the elements of the handler sequence in case an
    exception occurred.
    """

    if handler or not isinstance(second, Observable):
        return catch_handler(self, handler or second)

    return Observable.catch_exception([self, second])


@extensionclassmethod(Observable)
def catch_exception(cls, *args):
    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    1 - res = Observable.catch_exception(xs, ys, zs)
    2 - res = Observable.catch_exception([xs, ys, zs])

    Returns an observable sequence containing elements from consecutive
    source sequences until a source sequence terminates successfully.
    """

    if isinstance(args[0], list) or isinstance(args[0], Enumerable):
        sources = args[0]
    else:
        sources = list(args)

    #return Enumerable.catch_exception(Enumerable.for_each(sources))

    def subscribe(observer):
        e = iter(sources)
        is_disposed = [False]
        last_exception = [None]
        subscription = SerialDisposable()

        def action(action1, state=None):
            def on_error(exn):
                last_exception[0] = exn
                action1()

            if is_disposed[0]:
                return
            try:
                current = next(e)
            except StopIteration:
                if last_exception[0]:
                    observer.on_error(last_exception[0])
                else:
                    observer.on_completed()
            except Exception as ex:
                observer.on_error(ex)
            else:
                d = SingleAssignmentDisposable()
                subscription.disposable = d

                d.disposable = current.subscribe(
                    observer.on_next,
                    on_error,
                    observer.on_completed
                )

        cancelable = immediate_scheduler.schedule_recursive(action)

        def dispose():
            is_disposed[0] = True
        return CompositeDisposable(subscription, cancelable, Disposable.create(dispose))
    return AnonymousObservable(subscribe)
