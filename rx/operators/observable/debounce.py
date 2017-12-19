from rx.core import ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import timeout_scheduler


def debounce(self, duetime) -> ObservableBase:
    """Ignores values from an observable sequence which are followed by
    another value before duetime.

    Example:
    1 - res = source.debounce(5000) # 5 seconds

    Keyword arguments:
    duetime -- {Number} Duration of the throttle period for each value
        (specified as an integer denoting milliseconds).

    Returns the debounced sequence.
    """

    source = self

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or timeout_scheduler
        cancelable = SerialDisposable()
        has_value = [False]
        value = [None]
        _id = [0]

        def send(x):
            has_value[0] = True
            value[0] = x
            _id[0] += 1
            current_id = _id[0]
            d = SingleAssignmentDisposable()
            cancelable.disposable = d

            def action(scheduler, state=None):
                if has_value[0] and _id[0] == current_id:
                    observer.send(value[0])
                has_value[0] = False

            d.disposable = scheduler.schedule_relative(duetime, action)

        def throw(exception):
            cancelable.dispose()
            observer.throw(exception)
            has_value[0] = False
            _id[0] += 1

        def close():
            cancelable.dispose()
            if has_value[0]:
                observer.send(value[0])

            observer.close()
            has_value[0] = False
            _id[0] += 1

        subscription = source.subscribe_callbacks(send, throw, close, scheduler)
        return CompositeDisposable(subscription, cancelable)
    return AnonymousObservable(subscribe)

throttle_with_timeout = debounce


def throttle_with_selector(self, throttle_duration_selector) -> ObservableBase:
    """Ignores values from an observable sequence which are followed by
    another value within a computed throttle duration.

    1 - res = source.throttle_with_selector(lambda x: rx.Scheduler.timer(x+x))

    Keyword arguments:
    throttle_duration_selector -- Selector function to retrieve a sequence
        indicating the throttle duration for each given element.

    Returns the throttled sequence.
    """

    source = self

    def subscribe(observer, scheduler=None):
        cancelable = SerialDisposable()
        has_value = [False]
        value = [None]
        _id = [0]

        def send(x):
            throttle = None
            try:
                throttle = throttle_duration_selector(x)
            except Exception as e:
                observer.throw(e)
                return

            has_value[0] = True
            value[0] = x
            _id[0] += 1
            current_id = _id[0]
            d = SingleAssignmentDisposable()
            cancelable.disposable = d

            def send(x):
                if has_value[0] and _id[0] == current_id:
                    observer.send(value[0])

                has_value[0] = False
                d.dispose()

            def close():
                if has_value[0] and _id[0] == current_id:
                    observer.send(value[0])

                has_value[0] = False
                d.dispose()

            d.disposable = throttle.subscribe_callbacks(send, observer.throw,
                                              close, scheduler)

        def throw(e):
            cancelable.dispose()
            observer.throw(e)
            has_value[0] = False
            _id[0] += 1

        def close():
            cancelable.dispose()
            if has_value[0]:
                observer.send(value[0])

            observer.close()
            has_value[0] = False
            _id[0] += 1

        subscription = source.subscribe_callbacks(send, throw, close)
        return CompositeDisposable(subscription, cancelable)
    return AnonymousObservable(subscribe)
