from rx.core import Observable, ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable


def timeout_with_selector(source, first_timeout=None,
                        timeout_duration_mapper=None, other=None) -> ObservableBase:
    """Returns the source observable sequence, switching to the other
    observable sequence if a timeout is signaled.

    1 - res = source.timeout_with_selector(rx.Observable.timer(500))
    2 - res = source.timeout_with_selector(rx.Observable.timer(500),
                lambda x: rx.Observable.timer(200))
    3 - res = source.timeout_with_selector(rx.Observable.timer(500),
                lambda x: rx.Observable.timer(200)),
                rx.Observable.return_value(42))

    first_timeout -- [Optional] Observable sequence that represents the
        timeout for the first element. If not provided, this defaults to
        Observable.never().
    timeout_duration_mapper -- [Optional] Selector to retrieve an
        observable sequence that represents the timeout between the
        current element and the next element.
    other -- [Optional] Sequence to return in case of a timeout. If not
        provided, this is set to Observable.throw().

    Returns the source sequence switching to the other sequence in case
    of a timeout.
    """

    first_timeout = first_timeout or Observable.never()
    other = other or Observable.throw(Exception('Timeout'))

    def subscribe(observer, scheduler=None):
        subscription = SerialDisposable()
        timer = SerialDisposable()
        original = SingleAssignmentDisposable()

        subscription.disposable = original

        switched = False
        _id = [0]

        def set_timer(timeout):
            my_id = _id[0]

            def timer_wins():
                return _id[0] == my_id

            d = SingleAssignmentDisposable()
            timer.disposable = d

            def send(x):
                if timer_wins():
                    subscription.disposable = other.subscribe(observer, scheduler)

                d.dispose()

            def throw(e):
                if timer_wins():
                    observer.throw(e)

            def close():
                if timer_wins():
                    subscription.disposable = other.subscribe(observer)

            d.disposable = timeout.subscribe_callbacks(send, throw, close, scheduler)

        set_timer(first_timeout)

        def observer_wins():
            res = not switched
            if res:
                _id[0] += 1

            return res

        def send(x):
            if observer_wins():
                observer.send(x)
                timeout = None
                try:
                    timeout = timeout_duration_mapper(x)
                except Exception as e:
                    observer.throw(e)
                    return

                set_timer(timeout)

        def throw(error):
            if observer_wins():
                observer.throw(error)

        def close():
            if observer_wins():
                observer.close()

        original.disposable = source.subscribe_callbacks(send, throw, close, scheduler)
        return CompositeDisposable(subscription, timer)
    return AnonymousObservable(subscribe)
