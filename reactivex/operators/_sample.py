from typing import Any, TypeVar, cast

import reactivex
from reactivex import Observable, abc, typing
from reactivex.disposable import CompositeDisposable
from reactivex.internal import curry_flip

_T = TypeVar("_T")


def sample_observable(
    source: Observable[_T], sampler: Observable[Any]
) -> Observable[_T]:
    def subscribe(
        observer: abc.ObserverBase[_T], scheduler: abc.SchedulerBase | None = None
    ) -> abc.DisposableBase:
        at_end = False
        has_value = False
        value: _T = cast(_T, None)

        def sample_subscribe(_: Any = None) -> None:
            nonlocal has_value
            if has_value:
                has_value = False
                observer.on_next(value)

            if at_end:
                observer.on_completed()

        def on_next(new_value: _T):
            nonlocal has_value, value
            has_value = True
            value = new_value

        def on_completed():
            nonlocal at_end
            at_end = True

        return CompositeDisposable(
            source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            ),
            sampler.subscribe(
                sample_subscribe,
                observer.on_error,
                sample_subscribe,
                scheduler=scheduler,
            ),
        )

    return Observable(subscribe)


@curry_flip
def sample_(
    source: Observable[_T],
    sampler: typing.RelativeTime | Observable[Any],
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[_T]:
    """Samples the observable sequence at each interval.

    Examples:
        >>> res = source.pipe(sample(1.0))
        >>> res = sample(1.0)(source)
        >>> res = source.pipe(sample(other_observable))

    Args:
        source: Source sequence to sample.
        sampler: Interval or observable to sample at.
        scheduler: Scheduler to use.

    Returns:
        Sampled observable sequence.
    """

    if isinstance(sampler, abc.ObservableBase):
        return sample_observable(source, sampler)
    else:
        return sample_observable(
            source, reactivex.interval(sampler, scheduler=scheduler)
        )


__all__ = ["sample_"]
