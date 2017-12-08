from rx.core import Observable, AnonymousObservable, Disposable
from rx.disposables import SingleAssignmentDisposable, CompositeDisposable, SerialDisposable
from rx.concurrency import current_thread_scheduler


def concat(*args: Observable) -> Observable:
    """Concatenates all the observable sequences.

    1 - res = concat(xs, ys, zs)

    Returns an observable sequence that contains the elements of each given
    sequence, in sequential order.
    """

    sources = list(args)

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler

        subscription = SerialDisposable()
        cancelable = SerialDisposable()
        enum = iter(sources)
        is_disposed = []

        def action(action1, state=None):
            if is_disposed:
                return

            def close():
                cancelable.disposable = scheduler.schedule(action)

            try:
                current = next(enum)
            except StopIteration:
                observer.close()
            except Exception as ex:
                observer.throw(ex)
            else:
                d = SingleAssignmentDisposable()
                subscription.disposable = d
                d.disposable = current.subscribe_callbacks(observer.send, observer.throw, close, scheduler)

        cancelable.disposable = scheduler.schedule(action)

        def dispose():
            is_disposed.append(True)

        return CompositeDisposable(subscription, cancelable, Disposable.create(dispose))
    return AnonymousObservable(subscribe)
