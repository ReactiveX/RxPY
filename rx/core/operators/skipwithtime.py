from typing import Callable

from rx.core import Observable, AnonymousObservable, typing
from rx.disposable import CompositeDisposable
from rx.concurrency import timeout_scheduler

def _skip_with_time(duration: typing.RelativeTime, scheduler: typing.Scheduler = None) -> Callable[[Observable], Observable]:
    def skip_with_time(source: Observable) -> Observable:
        """Skips elements for the specified duration from the start of
        the observable source sequence.

        Args:
            >>> res = skip_with_time(5.0)

        Specifying a zero value for duration doesn't guarantee no
        elements will be dropped from the start of the source sequence.
        This is a side-effect of the asynchrony introduced by the
        scheduler, where the action that causes callbacks from the
        source sequence to be forwarded may not execute immediately,
        despite the zero due time.

        Errors produced by the source sequence are always forwarded to
        the result sequence, even if the error occurs before the
        duration.

        Args:
            duration: Duration for skipping elements from the start of
            the sequence.

        Returns:
            An observable sequence with the elements skipped during the
            specified duration from the start of the source sequence.
        """

        def subscribe(observer, scheduler_=None):
            _scheduler = scheduler or scheduler_ or timeout_scheduler
            open = [False]

            def action(scheduler, state):
                open[0] = True

            t = _scheduler.schedule_relative(duration, action)

            def on_next(x):
                if open[0]:
                    observer.on_next(x)

            d = source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler_)
            return CompositeDisposable(t, d)
        return AnonymousObservable(subscribe)
    return skip_with_time
