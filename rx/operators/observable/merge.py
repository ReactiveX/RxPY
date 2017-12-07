from rx.core import Scheduler, Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.concurrency import immediate_scheduler
from rx.internal import extensionmethod, extensionclassmethod


@extensionmethod(Observable, instancemethod=True)
def merge(self, *args, **kwargs):
    """Merges an observable sequence of observable sequences into an
    observable sequence, limiting the number of concurrent subscriptions
    to inner sequences. Or merges two observable sequences into a single
    observable sequence.

    1 - merged = sources.merge(1)
    2 - merged = source.merge(other_source)

    max_concurrent_or_other [Optional] Maximum number of inner observable
        sequences being subscribed to concurrently or the second
        observable sequence.

    Returns the observable sequence that merges the elements of the inner
    sequences.
    """

    if not isinstance(args[0], int):
        args = args + tuple([self])
        return Observable.merge(*args, **kwargs)

    max_concurrent = args[0]
    sources = self

    def subscribe(observer, scheduler=None):
        active_count = [0]
        group = CompositeDisposable()
        is_stopped = [False]
        q = []

        def subscribe(xs):
            subscription = SingleAssignmentDisposable()
            group.add(subscription)

            def close():
                group.remove(subscription)
                if len(q):
                    s = q.pop(0)
                    subscribe(s)
                else:
                    active_count[0] -= 1
                    if is_stopped[0] and active_count[0] == 0:
                        observer.close()

            subscription.disposable = xs.subscribe_callbacks(observer.send, observer.throw,
                                                             close)

        def send(inner_source):
            if active_count[0] < max_concurrent:
                active_count[0] += 1
                subscribe(inner_source)
            else:
                q.append(inner_source)

        def close():
            is_stopped[0] = True
            if active_count[0] == 0:
                observer.close()

        group.add(sources.subscribe_callbacks(send, observer.throw, close))
        return group
    return AnonymousObservable(subscribe)


@extensionclassmethod(Observable)  # noqa
def merge(cls, *args):
    """Merges all the observable sequences into a single observable
    sequence.

    1 - merged = rx.Observable.merge(xs, ys, zs)
    2 - merged = rx.Observable.merge([xs, ys, zs])

    Returns the observable sequence that merges the elements of the
    observable sequences.
    """

    sources = args[:]

    if isinstance(sources[0], list):
        sources = sources[0]

    return Observable.from_(sources).merge_all()


@extensionmethod(Observable, alias="merge_observable")
def merge_all(self):
    """Merges an observable sequence of observable sequences into an
    observable sequence.

    Returns the observable sequence that merges the elements of the inner
    sequences.
    """

    sources = self

    def subscribe(observer, scheduler=None):
        group = CompositeDisposable()
        is_stopped = [False]
        m = SingleAssignmentDisposable()
        group.add(m)

        def send(inner_source):
            inner_subscription = SingleAssignmentDisposable()
            group.add(inner_subscription)

            inner_source = Observable.from_future(inner_source)

            def send(x):
                observer.send(x)

            def close():
                group.remove(inner_subscription)
                if is_stopped[0] and len(group) == 1:
                    observer.close()

            disposable = inner_source.subscribe_callbacks(send, observer.throw, close, scheduler)
            inner_subscription.disposable = disposable

        def close():
            is_stopped[0] = True
            if len(group) == 1:
                observer.close()

        m.disposable = sources.subscribe_callbacks(send, observer.throw, close, scheduler)
        return group

    return AnonymousObservable(subscribe)
