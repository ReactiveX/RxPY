from datetime import timedelta
from typing import Any, Callable, List, Optional, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    RefCountDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import DELTA_ZERO, add_ref, synchronized
from reactivex.scheduler import TimeoutScheduler
from reactivex.subject import Subject

_T = TypeVar("_T")


def window_with_time_(
    timespan: typing.RelativeTime,
    timeshift: Optional[typing.RelativeTime] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    if timeshift is None:
        timeshift = timespan

    if not isinstance(timespan, timedelta):
        timespan = timedelta(seconds=timespan)
    if not isinstance(timeshift, timedelta):
        timeshift = timedelta(seconds=timeshift)

    def window_with_time(source: Observable[_T]) -> Observable[Observable[_T]]:
        def subscribe(
            observer: abc.ObserverBase[Observable[_T]],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            timer_d = SerialDisposable()
            next_shift = [timeshift]
            next_span = [timespan]
            total_time = [DELTA_ZERO]
            queue: List[Subject[_T]] = []

            group_disposable = CompositeDisposable(timer_d)
            ref_count_disposable = RefCountDisposable(group_disposable)

            def create_timer():
                m = SingleAssignmentDisposable()
                timer_d.disposable = m
                is_span = False
                is_shift = False

                if next_span[0] == next_shift[0]:
                    is_span = True
                    is_shift = True
                elif next_span[0] < next_shift[0]:
                    is_span = True
                else:
                    is_shift = True

                new_total_time = next_span[0] if is_span else next_shift[0]

                ts = new_total_time - total_time[0]
                total_time[0] = new_total_time
                if is_span:
                    next_span[0] += timeshift

                if is_shift:
                    next_shift[0] += timeshift

                @synchronized(source.lock)
                def action(scheduler: abc.SchedulerBase, state: Any = None):
                    s: Optional[Subject[_T]] = None

                    if is_shift:
                        s = Subject()
                        queue.append(s)
                        observer.on_next(add_ref(s, ref_count_disposable))

                    if is_span:
                        s = queue.pop(0)
                        s.on_completed()

                    create_timer()

                m.disposable = _scheduler.schedule_relative(ts, action)

            queue.append(Subject())
            observer.on_next(add_ref(queue[0], ref_count_disposable))
            create_timer()

            def on_next(x: _T) -> None:
                with source.lock:
                    for s in queue:
                        s.on_next(x)

            @synchronized(source.lock)
            def on_error(e: Exception) -> None:
                for s in queue:
                    s.on_error(e)

                observer.on_error(e)

            @synchronized(source.lock)
            def on_completed() -> None:
                for s in queue:
                    s.on_completed()

                observer.on_completed()

            group_disposable.add(
                source.subscribe(on_next, on_error, on_completed, scheduler=scheduler_)
            )
            return ref_count_disposable

        return Observable(subscribe)

    return window_with_time


__all__ = ["window_with_time_"]
