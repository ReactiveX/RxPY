from typing import Any, Callable, List, Optional, TypeVar

from rx.core import Observable, abc, typing
from rx.disposable import (
    CompositeDisposable,
    RefCountDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from rx.internal.utils import add_ref
from rx.scheduler import TimeoutScheduler
from rx.subject import Subject

_T = TypeVar("_T")


def window_with_time_or_count_(
    timespan: typing.RelativeTime,
    count: int,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    def window_with_time_or_count(source: Observable[_T]) -> Observable[Observable[_T]]:
        def subscribe(
            observer: abc.ObserverBase[Observable[_T]],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            n = [0]
            s: List[Optional[Subject[_T]]] = [None]
            timer_d = SerialDisposable()
            window_id = [0]
            group_disposable = CompositeDisposable(timer_d)
            ref_count_disposable = RefCountDisposable(group_disposable)

            def create_timer(_id):
                m = SingleAssignmentDisposable()
                timer_d.disposable = m

                def action(scheduler: abc.SchedulerBase, state: Any = None):
                    if _id != window_id[0]:
                        return

                    n[0] = 0
                    window_id[0] += 1
                    new_id = window_id[0]
                    s[0].on_completed()
                    s[0] = Subject()
                    observer.on_next(add_ref(s[0], ref_count_disposable))
                    create_timer(new_id)

                m.disposable = _scheduler.schedule_relative(timespan, action)

            s[0] = Subject()
            observer.on_next(add_ref(s[0], ref_count_disposable))
            create_timer(0)

            def on_next(x: _T) -> None:
                new_window = False
                new_id = 0

                s[0].on_next(x)
                n[0] += 1
                if n[0] == count:
                    new_window = True
                    n[0] = 0
                    window_id[0] += 1
                    new_id = window_id[0]
                    s[0].on_completed()
                    s[0] = Subject()
                    observer.on_next(add_ref(s[0], ref_count_disposable))

                if new_window:
                    create_timer(new_id)

            def on_error(e: Exception) -> None:
                s[0].on_error(e)
                observer.on_error(e)

            def on_completed() -> None:
                s[0].on_completed()
                observer.on_completed()

            group_disposable.add(
                source.subscribe_(on_next, on_error, on_completed, scheduler_)
            )
            return ref_count_disposable

        return Observable(subscribe)

    return window_with_time_or_count


__all__ = ["window_with_time_or_count_"]
