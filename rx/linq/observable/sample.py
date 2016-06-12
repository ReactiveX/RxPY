from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.concurrency import timeout_scheduler
from rx.internal import extensionmethod


def sample_observable(source, sampler):

    def subscribe(observer):
        at_end = [None]
        has_value = [None]
        value = [None]

        def sample_subscribe(x=None):
            if has_value[0]:
                has_value[0] = False
                observer.on_next(value[0])

            if at_end[0]:
                observer.on_completed()

        def on_next(new_value):
            has_value[0] = True
            value[0] = new_value

        def on_completed():
            at_end[0] = True

        return CompositeDisposable(
            source.subscribe(on_next, observer.on_error, on_completed),
            sampler.subscribe(sample_subscribe, observer.on_error, sample_subscribe)
        )
    return AnonymousObservable(subscribe)


@extensionmethod(Observable, alias="throttle_last")
def sample(self, interval=None, sampler=None, scheduler=None):
    """Samples the observable sequence at each interval.

    Examples::

        # Sampler tick sequence
        res = source.sample(sample_observable)
        # 5 seconds (5000 milliseconds)
        res = source.sample(5000)
        # 5 seconds
        res = source.sample(5000, rx.scheduler.timeout)

    Arguments:

      source (Observable): Source sequence to sample.
      
    Keyword Arguments:
      interval (int): Interval at which to sample (specified as an integer
        denoting milliseconds).
      scheduler (Secheduler): Scheduler to run the sampling timer on. If not
        specified, the timeout scheduler is used.

    Returns:
      (Observable): sampled observable sequence.
    """

    scheduler = scheduler or timeout_scheduler
    if interval is not None:
        return sample_observable(self, Observable.interval(interval, scheduler=scheduler))

    return sample_observable(self, sampler)
