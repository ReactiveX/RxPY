from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import extensionmethod, extensionclassmethod


@extensionmethod(Observable, instancemethod=True)
def zip(self, *args):
    """Merges the specified observable sequences into one observable
    sequence by using the selector function whenever all of the observable
    sequences or an array have produced an element at a corresponding index.

    The last element in the arguments must be a function to invoke for each
    series of elements at corresponding indexes in the sources.

    1 - res = obs1.zip(obs2, fn)
    2 - res = x1.zip([1,2,3], fn)

    Returns an observable sequence containing the result of combining
    elements of the sources using the specified result selector function.
    """

    parent = self
    sources = list(args)
    result_selector = sources.pop()
    sources.insert(0, parent)

    if args and isinstance(args[0], list):
        return _zip_list(self, *args)

    def subscribe(observer, scheduler=None):
        n = len(sources)
        queues = [[] for _ in range(n)]
        is_done = [False] * n

        def next(i):
            if all([len(q) for q in queues]):
                try:
                    queued_values = [x.pop(0) for x in queues]
                    res = result_selector(*queued_values)
                except Exception as ex:
                    observer.throw(ex)
                    return

                observer.send(res)
            elif all([x for j, x in enumerate(is_done) if j != i]):
                observer.close()

        def done(i):
            is_done[i] = True
            if all(is_done):
                observer.close()

        subscriptions = [None]*n

        def func(i):
            source = sources[i]
            sad = SingleAssignmentDisposable()
            source = Observable.from_future(source)

            def send(x):
                queues[i].append(x)
                next(i)

            sad.disposable = source.subscribe_callbacks(send, observer.throw, lambda: done(i))
            subscriptions[i] = sad
        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)
    return AnonymousObservable(subscribe)


@extensionclassmethod(Observable)
def zip(cls, *args):
    """Merges the specified observable sequences into one observable
    sequence by using the selector function whenever all of the observable
    sequences have produced an element at a corresponding index.

    The last element in the arguments must be a function to invoke for each
    series of elements at corresponding indexes in the sources.

    Arguments:
    args -- Observable sources.

    Returns an observable {Observable} sequence containing the result of
    combining elements of the sources using the specified result selector
    function.
    """

    first = args[0]
    return first.zip(*args[1:])


def _zip_list(source, second, result_selector):
    first = source

    def subscribe(observer, scheduler=None):
        length = len(second)
        index = [0]

        def send(left):
            if index[0] < length:
                right = second[index[0]]
                index[0] += 1
                try:
                    result = result_selector(left, right)
                except Exception as ex:
                    observer.throw(ex)
                    return
                observer.send(result)
            else:
                observer.close()

        return first.subscribe_callbacks(send, observer.throw, observer.close)
    return AnonymousObservable(subscribe)
