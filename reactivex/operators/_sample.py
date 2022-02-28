from typing import Any, Callable, Optional, TypeVar, Union, cast

import reactivex
from reactivex import Observable, abc, typing
from reactivex.disposable import CompositeDisposable

_T = TypeVar("_T")


def sample_observable(
    source: Observable[_T], sampler: Observable[Any]
) -> Observable[_T]:
    def subscribe(
        observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase] = None
    ):
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


def sample_(
    sampler: Union[typing.RelativeTime, Observable[Any]],
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def sample(source: Observable[_T]) -> Observable[_T]:
        """Samples the observable sequence at each interval.

        Examples:
            >>> res = sample(source)

        Args:
            source: Source sequence to sample.

        Returns:
            Sampled observable sequence.
        """

        if isinstance(sampler, abc.ObservableBase):
            return sample_observable(source, sampler)
        else:
            return sample_observable(
                source, reactivex.interval(sampler, scheduler=scheduler)
            )

    return sample


__all__ = ["sample_"]
