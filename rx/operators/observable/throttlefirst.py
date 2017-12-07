from rx.core import Observable, AnonymousObservable
from rx.concurrency import timeout_scheduler
from rx.internal import extensionmethod


@extensionmethod(Observable)
def throttle_first(self, window_duration, scheduler=None):
    """Returns an Observable that emits only the first item emitted by the
    source Observable during sequential time windows of a specified
    duration.

    Keyword arguments:
    window_duration -- {timedelta} time to wait before emitting another item
        after emitting the last item.
    scheduler -- {Scheduler} [Optional] the Scheduler to use internally to
        manage the timers that handle timeout for each item. If not
        provided, defaults to Scheduler.timeout.
    Returns {Observable} An Observable that performs the throttle operation.
    """

    scheduler = scheduler or timeout_scheduler
    duration = scheduler.to_timedelta(+window_duration or 0)
    if duration <= scheduler.to_timedelta(0):
        raise ValueError('window_duration cannot be less or equal zero.')

    source = self

    def subscribe(observer, scheduler=None):
        last_send = [0]

        def send(x):
            emit = False
            now = scheduler.now

            with self.lock:
                if not last_send[0] or now - last_send[0] >= duration:
                    last_send[0] = now
                    emit = True
            if emit:
                observer.send(x)

        return source.subscribe_callbacks(send, observer.throw, observer.close)
    return AnonymousObservable(subscribe)
