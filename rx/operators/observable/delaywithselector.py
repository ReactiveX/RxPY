from rx.core import ObservableBase, AnonymousObservable, typing
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable


def delay_with_selector(self, subscription_delay=None,
                        delay_duration_selector=None) -> ObservableBase:
    """Time shifts the observable sequence based on a subscription delay
    and a delay selector function for each element.

    # with selector only
    1 - res = source.delay_with_selector(lambda x: Scheduler.timer(5000))
    # with delay and selector
    2 - res = source.delay_with_selector(Observable.timer(2000),
                                         lambda x: Observable.timer(x))

    subscription_delay -- [Optional] Sequence indicating the delay for the
        subscription to the source.
    delay_duration_selector [Optional] Selector function to retrieve a
        sequence indicating the delay for each given element.

    Returns time-shifted sequence.
    """

    source = self
    sub_delay, selector = None, None

    if isinstance(subscription_delay, typing.Observable):
        selector = delay_duration_selector
        sub_delay = subscription_delay
    else:
        selector = subscription_delay

    def subscribe(observer, scheduler=None):
        delays = CompositeDisposable()
        at_end = [False]

        def done():
            if (at_end[0] and delays.length == 0):
                observer.close()

        subscription = SerialDisposable()

        def start():
            def send(x):
                try:
                    delay = selector(x)
                except Exception as error:
                    observer.throw(error)
                    return

                d = SingleAssignmentDisposable()
                delays.add(d)

                def send(_):
                    observer.send(x)
                    delays.remove(d)
                    done()

                def close():
                    observer.send(x)
                    delays.remove(d)
                    done()

                d.disposable = delay.subscribe_callbacks(send, observer.throw, close, scheduler)

            def close():
                at_end[0] = True
                subscription.dispose()
                done()

            subscription.disposable = source.subscribe_callbacks(send, observer.throw, close, scheduler)

        if not sub_delay:
            start()
        else:
            subscription.disposable(sub_delay.subscribe_callbacks(
                lambda _: start(),
                observer.throw,
                start))

        return CompositeDisposable(subscription, delays)
    return AnonymousObservable(subscribe)
