from rx.core import ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import timeout_scheduler


def debounce(self, duetime) -> ObservableBase:
    """Ignores values from an observable sequence which are followed by
    another value before duetime.

    Example:
        >>> res = source.debounce(5000) # 5 seconds

    Args:
        duetime: Duration of the throttle period for each value
        (specified as an integer denoting milliseconds).

    Returns:
        The debounced sequence.
    """

    source = self

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or timeout_scheduler
        cancelable = SerialDisposable()
        has_value = [False]
        value = [None]
        _id = [0]

        def on_next(x):
            has_value[0] = True
            value[0] = x
            _id[0] += 1
            current_id = _id[0]
            d = SingleAssignmentDisposable()
            cancelable.disposable = d

            def action(scheduler, state=None):
                if has_value[0] and _id[0] == current_id:
                    observer.on_next(value[0])
                has_value[0] = False

            d.disposable = scheduler.schedule_relative(duetime, action)

        def on_error(exception):
            cancelable.dispose()
            observer.on_error(exception)
            has_value[0] = False
            _id[0] += 1

        def on_completed():
            cancelable.dispose()
            if has_value[0]:
                observer.on_next(value[0])

            observer.on_completed()
            has_value[0] = False
            _id[0] += 1

        subscription = source.subscribe_(on_next, on_error, on_completed, scheduler)
        return CompositeDisposable(subscription, cancelable)
    return AnonymousObservable(subscribe)

throttle_with_timeout = debounce


def throttle_with_mapper(self, throttle_duration_mapper) -> ObservableBase:
    """Ignores values from an observable sequence which are followed by
    another value within a computed throttle duration.

    Example:
        >>> res = source.throttle_with_mapper(lambda x: rx.Scheduler.timer(x+x))

    Args:
        throttle_duration_mapper: Selector function to retrieve a
        sequence indicating the throttle duration for each given
        element.

    Returns:
        The throttled sequence.
    """

    source = self

    def subscribe(observer, scheduler=None):
        cancelable = SerialDisposable()
        has_value = [False]
        value = [None]
        _id = [0]

        def on_next(x):
            throttle = None
            try:
                throttle = throttle_duration_mapper(x)
            except Exception as e:
                observer.on_error(e)
                return

            has_value[0] = True
            value[0] = x
            _id[0] += 1
            current_id = _id[0]
            d = SingleAssignmentDisposable()
            cancelable.disposable = d

            def on_next(x):
                if has_value[0] and _id[0] == current_id:
                    observer.on_next(value[0])

                has_value[0] = False
                d.dispose()

            def on_completed():
                if has_value[0] and _id[0] == current_id:
                    observer.on_next(value[0])

                has_value[0] = False
                d.dispose()

            d.disposable = throttle.subscribe_(on_next, observer.on_error,
                                              on_completed, scheduler)

        def on_error(e):
            cancelable.dispose()
            observer.on_error(e)
            has_value[0] = False
            _id[0] += 1

        def on_completed():
            cancelable.dispose()
            if has_value[0]:
                observer.on_next(value[0])

            observer.on_completed()
            has_value[0] = False
            _id[0] += 1

        subscription = source.subscribe_(on_next, on_error, on_completed)
        return CompositeDisposable(subscription, cancelable)
    return AnonymousObservable(subscribe)
