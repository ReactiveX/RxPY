from typing import Union, Iterable, Any
from rx.core import Observable, ObservableBase, AnonymousObservable
from rx.core.typing import Selector
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable


def zip(*args: Union[Iterable[Any], ObservableBase],  # pylint: disable=W0622
        result_selector: Selector = None) -> ObservableBase:
    """Merges the specified observable sequences into one observable
    sequence by using the selector function whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    The last element in the arguments must be a function to invoke for
    each series of elements at corresponding indexes in the sources.

    1 - res = zip(obs1, obs2, result_selector=fn)
    2 - res = zip(xs, [1,2,3], result_selector=fn)

    Arguments:
    args -- Observable sources.

    Returns an observable sequence containing the result of
    combining elements of the sources using the specified result
    selector function.
    """

    if len(args) == 2 and isinstance(args[1], Iterable):
        return _zip_list(args[0], args[1], result_selector=result_selector)

    sources = list(args)

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

            sad.disposable = source.subscribe_callbacks(send, observer.throw, lambda: done(i), scheduler)
            subscriptions[i] = sad
        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)
    return AnonymousObservable(subscribe)

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

        return first.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
