from typing import Union, Callable
from datetime import timedelta

from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.concurrency import timeout_scheduler


def _take_with_time(duration: Union[timedelta, int]) -> Callable[[Observable], Observable]:
    def take_with_time(source: Observable) -> Observable:
        """Takes elements for the specified duration from the start of
        the observable source sequence.

        Example:
            >>> res = take_with_time(source)

        This operator accumulates a queue with a length enough to store
        elements received during the initial duration window. As more
        elements are received, elements older than the specified
        duration are taken from the queue and produced on the result
        sequence. This causes elements to be delayed with duration.

        Args:
            source: Source observable to take elements from.

        Returns:
            An observable sequence with the elements taken during the
            specified duration from the start of the source sequence.
        """

        def subscribe(observer, scheduler=None):
            scheduler = scheduler or timeout_scheduler

            def action(scheduler, state):
                observer.on_completed()

            disposable = scheduler.schedule_relative(duration, action)
            return CompositeDisposable(disposable, source.subscribe(observer, scheduler))
        return AnonymousObservable(subscribe)
    return take_with_time
