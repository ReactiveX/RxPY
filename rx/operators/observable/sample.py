from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.concurrency import timeout_scheduler
from rx.internal import extensionmethod


def sample_observable(source, sampler):

    def subscribe(observer, scheduler=None):
        at_end = [None]
        has_value = [None]
        value = [None]

        def sample_subscribe(x=None):
            if has_value[0]:
                has_value[0] = False
                observer.send(value[0])

            if at_end[0]:
                observer.close()

        def send(new_value):
            has_value[0] = True
            value[0] = new_value

        def close():
            at_end[0] = True

        return CompositeDisposable(
            source.subscribe_callbacks(send, observer.throw, close),
            sampler.subscribe_callbacks(sample_subscribe, observer.throw, sample_subscribe)
        )
    return AnonymousObservable(subscribe)


@extensionmethod(Observable, alias="throttle_last")
def sample(self, interval=None, sampler=None, scheduler=None):
    """Samples the observable sequence at each interval.

    1 - res = source.sample(sample_observable) # Sampler tick sequence
    2 - res = source.sample(5000) # 5 seconds
    2 - res = source.sample(5000, rx.scheduler.timeout) # 5 seconds

    Keyword arguments:
    source -- Source sequence to sample.
    interval -- Interval at which to sample (specified as an integer
        denoting milliseconds).
    scheduler -- [Optional] Scheduler to run the sampling timer on. If not
        specified, the timeout scheduler is used.

    Returns sampled observable sequence.
    """

    scheduler = scheduler or timeout_scheduler
    if interval is not None:
        return sample_observable(self, Observable.interval(interval, scheduler=scheduler))

    return sample_observable(self, sampler)
