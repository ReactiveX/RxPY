from rx.core import ObservableBase, AnonymousObservable, typing
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable


def delay_with_selector(self, subscription_delay=None,
                        delay_duration_mapper=None) -> ObservableBase:
    """Time shifts the observable sequence based on a subscription delay
    and a delay mapper function for each element.

    # with mapper only
    1 - res = source.delay_with_selector(lambda x: Scheduler.timer(5000))
    # with delay and mapper
    2 - res = source.delay_with_selector(Observable.timer(2000),
                                         lambda x: Observable.timer(x))

    subscription_delay -- [Optional] Sequence indicating the delay for the
        subscription to the source.
    delay_duration_mapper [Optional] Selector function to retrieve a
        sequence indicating the delay for each given element.

    Returns time-shifted sequence.
    """

    source = self
    sub_delay, mapper = None, None

    if isinstance(subscription_delay, typing.Observable):
        mapper = delay_duration_mapper
        sub_delay = subscription_delay
    else:
        mapper = subscription_delay

    def subscribe(observer, scheduler=None):
        delays = CompositeDisposable()
        at_end = [False]

        def done():
            if (at_end[0] and delays.length == 0):
                observer.on_completed()

        subscription = SerialDisposable()

        def start():
            def on_next(x):
                try:
                    delay = mapper(x)
                except Exception as error:
                    observer.on_error(error)
                    return

                d = SingleAssignmentDisposable()
                delays.add(d)

                def on_next(_):
                    observer.on_next(x)
                    delays.remove(d)
                    done()

                def on_completed():
                    observer.on_next(x)
                    delays.remove(d)
                    done()

                d.disposable = delay.subscribe_(on_next, observer.on_error, on_completed, scheduler)

            def on_completed():
                at_end[0] = True
                subscription.dispose()
                done()

            subscription.disposable = source.subscribe_(on_next, observer.on_error, on_completed, scheduler)

        if not sub_delay:
            start()
        else:
            subscription.disposable(sub_delay.subscribe_(
                lambda _: start(),
                observer.on_error,
                start))

        return CompositeDisposable(subscription, delays)
    return AnonymousObservable(subscribe)
