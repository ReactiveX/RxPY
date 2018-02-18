from rx.core import Observable, ObservableBase, AnonymousObservable, Disposable, typing
from rx.disposables import SingleAssignmentDisposable, \
    CompositeDisposable, SerialDisposable
from rx.concurrency import current_thread_scheduler
from rx.internal import Iterable
from rx.internal.utils import is_future


def catch_handler(source, handler) -> ObservableBase:
    def subscribe(observer, scheduler=None):
        d1 = SingleAssignmentDisposable()
        subscription = SerialDisposable()

        subscription.disposable = d1

        def on_error(exception):
            try:
                result = handler(exception)
            except Exception as ex:
                observer.on_error(ex)
                return

            result = Observable.from_future(result) if is_future(result) else result
            d = SingleAssignmentDisposable()
            subscription.disposable = d
            d.disposable = result.subscribe(observer, scheduler)

        d1.disposable = source.subscribe_(
            observer.on_next,
            on_error,
            observer.on_completed,
            scheduler
        )
        return subscription
    return AnonymousObservable(subscribe)


def catch_exception(source, second=None, handler=None) -> ObservableBase:
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

    if handler or not isinstance(second, typing.Observable):
        return catch_handler(source, handler or second)

    return Observable.catch_exception([source, second])

def catch_exception_(*args) -> ObservableBase:
    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    1 - res = Observable.catch_exception(xs, ys, zs)
    2 - res = Observable.catch_exception([xs, ys, zs])

    Returns an observable sequence containing elements from consecutive
    source sequences until a source sequence terminates successfully.
    """

    if isinstance(args[0], list) or isinstance(args[0], Iterable):
        sources = args[0]
    else:
        sources = list(args)

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler

        subscription = SerialDisposable()
        cancelable = SerialDisposable()
        last_exception = [None]
        is_disposed = []
        e = iter(sources)

        def action(action1, state=None):
            def on_error(exn):
                last_exception[0] = exn
                cancelable.disposable = scheduler.schedule(action)

            if is_disposed:
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
                d.disposable = current.subscribe_(observer.on_next, on_error, observer.on_completed, scheduler)

        cancelable.disposable = scheduler.schedule(action)

        def dispose():
            is_disposed.append(True)
        return CompositeDisposable(subscription, cancelable, Disposable.create(dispose))
    return AnonymousObservable(subscribe)
