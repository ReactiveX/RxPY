from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import extensionmethod, extensionclassmethod


@extensionmethod(Observable, instancemethod=True)
def combine_latest(self, *args):
    """Merges the specified observable sequences into one observable
    sequence by using the selector function whenever any of the
    observable sequences produces an element. This can be in the form of
    an argument list of observables or an array.

    1 - obs = observable.combine_latest(obs1, obs2, obs3,
                                        lambda o1, o2, o3: o1 + o2 + o3)
    2 - obs = observable.combine_latest([obs1, obs2, obs3],
                                        lambda o1, o2, o3: o1 + o2 + o3)

    Returns an observable sequence containing the result of combining
    elements of the sources using the specified result selector
    function.
    """

    args = list(args)
    if args and isinstance(args[0], list):
        args = args[0]

    args.insert(0, self)

    return Observable.combine_latest(*args)


@extensionclassmethod(Observable)  # noqa
def combine_latest(cls, *args):
    """Merges the specified observable sequences into one observable
    sequence by using the selector function whenever any of the
    observable sequences produces an element.

    1 - obs = Observable.combine_latest(obs1, obs2, obs3,
                                       lambda o1, o2, o3: o1 + o2 + o3)
    2 - obs = Observable.combine_latest([obs1, obs2, obs3],
                                        lambda o1, o2, o3: o1 + o2 + o3)

    Returns an observable sequence containing the result of combining
    elements of the sources using the specified result selector
    function.
    """

    args = list(args)
    result_selector = args.pop()

    if isinstance(args[0], list):
        args = args[0]
    parent = args[0]

    def subscribe(observer):
        n = len(args)
        has_value = [False] * n
        has_value_all = [False]
        is_done = [False] * n
        values = [None] * n

        def next(i):
            has_value[i] = True

            if has_value_all[0] or all(has_value):
                try:
                    res = result_selector(*values)
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

            subscriptions[i].disposable = args[i].subscribe_callbacks(send, observer.throw, close)

        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)
    return AnonymousObservable(subscribe)
