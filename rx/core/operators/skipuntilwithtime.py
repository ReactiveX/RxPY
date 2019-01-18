from datetime import datetime
from typing import Union, Callable

from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.concurrency import timeout_scheduler


def _skip_until_with_time(start_time: Union[datetime, int]) -> Callable[[Observable], Observable]:
    def skip_until_with_time(source: Observable) -> Observable:
        """Skips elements from the observable source sequence until the
        specified start time.

        Errors produced by the source sequence are always forwarded to
        the result sequence, even if the error occurs before the start
        time.

        Examples:
            >>> res = source.skip_until_with_time(datetime)
            >>> res = source.skip_until_with_time(5000)

        Args:
            start_time -- Time to start taking elements from the source
                sequence. If this value is less than or equal to
                `datetime.utcnow`, no elements will be skipped.

        Returns:
            An observable sequence with the elements skipped until the
            specified start time.
        """

        if isinstance(start_time, datetime):
            scheduler_method = 'schedule_absolute'
        else:
            scheduler_method = 'schedule_relative'

        def subscribe(observer, scheduler=None):
            scheduler = scheduler or timeout_scheduler
            open = [False]

            def on_next(x):
                if open[0]:
                    observer.on_next(x)
            subscription = source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)

            def action(scheduler, state):
                open[0] = True
            disposable = getattr(scheduler, scheduler_method)(start_time, action)
            return CompositeDisposable(disposable, subscription)
        return AnonymousObservable(subscribe)
    return skip_until_with_time
