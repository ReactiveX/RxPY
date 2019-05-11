from typing import Callable, Optional

import rx
from rx.core import Observable, typing
from rx.disposable import CompositeDisposable


def sample_observable(source, sampler):
    def subscribe(observer, scheduler=None):
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
            source.subscribe_(on_next, observer.on_error, on_completed, scheduler),
            sampler.subscribe_(sample_subscribe, observer.on_error, sample_subscribe, scheduler)
        )
    return Observable(subscribe)


def _sample(interval=None, sampler=None, scheduler: Optional[typing.Scheduler] = None) -> Callable[[Observable], Observable]:
    def sample(source: Observable) -> Observable:
        """Samples the observable sequence at each interval.

        Examples:
            >>> res = sample(source)

        Args:
            source: Source sequence to sample.

        Returns:
            Sampled observable sequence.
        """

        if interval is None:
            return sample_observable(source, sampler)

        return sample_observable(source, rx.interval(interval, scheduler=scheduler))
    return sample
