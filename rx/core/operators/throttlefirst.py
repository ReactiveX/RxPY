from typing import Union, Callable
from datetime import timedelta

from rx.core import Observable, AnonymousObservable
from rx.concurrency import timeout_scheduler


def _throttle_first(window_duration: Union[timedelta, int]) -> Callable[[Observable], Observable]:
    def throttle_first(source: Observable) -> Observable:
        """Returns an observable that emits only the first item emitted
        by the source Observable during sequential time windows of a
        specifiedduration.

        Args:
            source: Source observable to throttle.

        Returns:
            An Observable that performs the throttle operation.
        """
        def subscribe(observer, scheduler=None):
            scheduler = scheduler or timeout_scheduler

            duration = scheduler.to_timedelta(+window_duration or 0)
            if duration <= scheduler.to_timedelta(0):
                raise ValueError('window_duration cannot be less or equal zero.')
            last_on_next = [0]

            def on_next(x):
                emit = False
                now = scheduler.now

                with source.lock:
                    if not last_on_next[0] or now - last_on_next[0] >= duration:
                        last_on_next[0] = now
                        emit = True
                if emit:
                    observer.on_next(x)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler=scheduler)
        return AnonymousObservable(subscribe)
    return throttle_first
