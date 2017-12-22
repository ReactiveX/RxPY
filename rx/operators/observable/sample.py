from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable


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
            source.subscribe_callbacks(send, observer.throw, close, scheduler),
            sampler.subscribe_callbacks(sample_subscribe, observer.throw, sample_subscribe, scheduler)
        )
    return AnonymousObservable(subscribe)


def sample(source, interval=None, sampler=None):
    """Samples the observable sequence at each interval.

    1 - res = source.sample(sample_observable) # Sampler tick sequence
    2 - res = source.sample(5000) # 5 seconds

    Keyword arguments:
    source -- Source sequence to sample.
    interval -- Interval at which to sample (specified as an integer
        denoting milliseconds).

    Returns sampled observable sequence.
    """

    if interval is not None:
        return sample_observable(source, Observable.interval(interval))

    return sample_observable(source, sampler)
