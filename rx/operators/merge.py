from rx.core import Observable, ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.concurrency import synchronized
from rx.internal.utils import is_future

from .fromiterable import from_iterable


def merge(source, *args, max_concurrent=None):
    """Merges an observable sequence of observable sequences into an
    observable sequence, limiting the number of concurrent subscriptions
    to inner sequences. Or merges two observable sequences into a single
    observable sequence.

    1 - merged = sources.merge(max_concurrent=1)
    2 - merged = source.merge(other_source)

    Keyword arguments:
    max_concurrent -- [Optional] Maximum number of inner observable
        sequences being subscribed to concurrently or the second
        observable sequence.

    Returns the observable sequence that merges the elements of the
    inner sequences.
    """

    if max_concurrent is None:
        args = tuple([source]) + args
        return Observable.merge(*args)

    def subscribe(observer, scheduler=None):
        active_count = [0]
        group = CompositeDisposable()
        is_stopped = [False]
        queue = []

        def subscribe(xs):
            subscription = SingleAssignmentDisposable()
            group.add(subscription)

            @synchronized(source.lock)
            def on_completed():
                group.remove(subscription)
                if queue:
                    s = queue.pop(0)
                    subscribe(s)
                else:
                    active_count[0] -= 1
                    if is_stopped[0] and active_count[0] == 0:
                        observer.on_completed()

            on_next = synchronized(source.lock)(observer.on_next)
            on_error = synchronized(source.lock)(observer.on_error)
            subscription.disposable = xs.subscribe_(on_next, on_error, on_completed, scheduler)

        def on_next(inner_source):
            if active_count[0] < max_concurrent:
                active_count[0] += 1
                subscribe(inner_source)
            else:
                queue.append(inner_source)

        def on_completed():
            is_stopped[0] = True
            if active_count[0] == 0:
                observer.on_completed()

        group.add(source.subscribe_(on_next, observer.on_error, on_completed, scheduler))
        return group
    return AnonymousObservable(subscribe)


def merge_(*args):
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

    return from_iterable(sources).pipe(merge_all)


def merge_all(source: ObservableBase) -> ObservableBase:
    """Merges an observable sequence of observable sequences into an
    observable sequence.

    Returns the observable sequence that merges the elements of the inner
    sequences.
    """

    def subscribe(observer, scheduler=None):
        group = CompositeDisposable()
        is_stopped = [False]
        m = SingleAssignmentDisposable()
        group.add(m)

        def on_next(inner_source):
            inner_subscription = SingleAssignmentDisposable()
            group.add(inner_subscription)

            inner_source = Observable.from_future(inner_source) if is_future(inner_source) else inner_source

            @synchronized(source.lock)
            def on_completed():
                group.remove(inner_subscription)
                if is_stopped[0] and len(group) == 1:
                    observer.on_completed()

            on_next = synchronized(source.lock)(observer.on_next)
            on_error = synchronized(source.lock)(observer.on_error)
            disposable = inner_source.subscribe_(on_next, on_error, on_completed, scheduler)
            inner_subscription.disposable = disposable

        def on_completed():
            is_stopped[0] = True
            if len(group) == 1:
                observer.on_completed()

        m.disposable = source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return group

    return AnonymousObservable(subscribe)
