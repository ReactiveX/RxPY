from typing import Any, Callable, Iterable, Union
from rx.core import ObservableBase, AnonymousObservable, typing
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable


def combine_latest(observables: Union[ObservableBase, Iterable[ObservableBase]],
                   mapper: Callable[[Any], Any]) -> ObservableBase:
    """Merges the specified observable sequences into one observable
    sequence by using the mapper function whenever any of the
    observable sequences produces an element.

    1 - obs = Observable.combine_latest(obs1, obs2, obs3,
                                       lambda o1, o2, o3: o1 + o2 + o3)
    2 - obs = Observable.combine_latest([obs1, obs2, obs3],
                                        lambda o1, o2, o3: o1 + o2 + o3)

    Returns an observable sequence containing the result of combining
    elements of the sources using the specified result mapper
    function.
    """
    if isinstance(observables, typing.Observable):
        observables = [observables]

    args = list(observables)
    result_mapper = mapper
    parent = args[0]

    def subscribe(observer, scheduler=None):
        n = len(args)
        has_value = [False] * n
        has_value_all = [False]
        is_done = [False] * n
        values = [None] * n

        def next(i):
            has_value[i] = True

            if has_value_all[0] or all(has_value):
                try:
                    res = result_mapper(*values)
                except Exception as ex:
                    observer.throw(ex)
                    return

                observer.send(res)
            elif all([x for j, x in enumerate(is_done) if j != i]):
                observer.close()

            has_value_all[0] = all(has_value)

        def done(i):
            is_done[i] = True
            if all(is_done):
                observer.close()

        subscriptions = [None] * n

        def func(i):
            subscriptions[i] = SingleAssignmentDisposable()

            def send(x):
                with parent.lock:
                    values[i] = x
                    next(i)

            def close():
                with parent.lock:
                    done(i)

            subscriptions[i].disposable = args[i].subscribe_(send, observer.throw,
                                                                      close, scheduler)

        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)
    return AnonymousObservable(subscribe)
