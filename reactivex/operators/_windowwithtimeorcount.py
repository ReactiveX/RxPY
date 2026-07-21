from typing import Any, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    RefCountDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import add_ref, curry_flip
from reactivex.scheduler import TimeoutScheduler
from reactivex.subject import Subject

_T = TypeVar("_T")


@curry_flip
def window_with_time_or_count_(
    source: Observable[_T],
    timespan: typing.RelativeTime,
    count: int,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[Observable[_T]]:
    """Projects each element of an observable sequence into zero or more
    windows which are produced based on timing information and element count.

    Examples:
        >>> res = source.pipe(window_with_time_or_count(1.0, 10))
        >>> res = window_with_time_or_count(1.0, 10)(source)

    Args:
        source: Source observable to window.
        timespan: Maximum time length of a window.
        count: Maximum element count of a window.
        scheduler: Scheduler to use for timing.

    Returns:
        An observable sequence of windows.
    """

    def subscribe(
        observer: abc.ObserverBase[Observable[_T]],
        scheduler_: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

        n: int = 0
        s: Subject[_T] = Subject()
        timer_d = SerialDisposable()
        window_id = 0
        group_disposable = CompositeDisposable(timer_d)
        ref_count_disposable = RefCountDisposable(group_disposable)

        def create_timer(_id: int):
            nonlocal n, s, window_id
            m = SingleAssignmentDisposable()
            timer_d.disposable = m

            def action(scheduler: abc.SchedulerBase, state: Any = None):
                nonlocal n, s, window_id
                if _id != window_id:
                    return

                n = 0
                window_id += 1
                new_id = window_id
                s.on_completed()
                s = Subject()
                observer.on_next(add_ref(s, ref_count_disposable))
                create_timer(new_id)

            m.disposable = _scheduler.schedule_relative(timespan, action)

        observer.on_next(add_ref(s, ref_count_disposable))
        create_timer(0)

        def on_next(x: _T) -> None:
            nonlocal n, s, window_id
            new_window = False
            new_id = 0

            s.on_next(x)
            n += 1
            if n == count:
                new_window = True
                n = 0
                window_id += 1
                new_id = window_id
                s.on_completed()
                s = Subject()
                observer.on_next(add_ref(s, ref_count_disposable))

            if new_window:
                create_timer(new_id)

        def on_error(e: Exception) -> None:
            s.on_error(e)
            observer.on_error(e)

        def on_completed() -> None:
            s.on_completed()
            observer.on_completed()

        group_disposable.add(
            source.subscribe(on_next, on_error, on_completed, scheduler=scheduler_)
        )
        return ref_count_disposable

    return Observable(subscribe)


__all__ = ["window_with_time_or_count_"]
