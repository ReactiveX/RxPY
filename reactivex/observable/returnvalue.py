from collections.abc import Callable
from typing import Any, TypeVar

from reactivex import Observable, abc
from reactivex.scheduler import CurrentThreadScheduler

_T = TypeVar("_T")


def return_value_(
    value: _T, scheduler: abc.SchedulerBase | None = None
) -> Observable[_T]:
    """Returns an observable sequence that contains a single element,
    using the specified scheduler to send out observer messages.
    There is an alias called 'just'.

    Examples:
        >>> res = return(42)
        >>> res = return(42, rx.Scheduler.timeout)

    Args:
        value: Single element in the resulting observable sequence.

    Returns:
        An observable sequence containing the single specified
        element.
    """

    def subscribe(
        observer: abc.ObserverBase[_T], scheduler_: abc.SchedulerBase | None = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or CurrentThreadScheduler.singleton()

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            observer.on_next(value)
            observer.on_completed()

        return _scheduler.schedule(action)

    return Observable(subscribe)


def from_callable_(
    supplier: Callable[[], _T], scheduler: abc.SchedulerBase | None = None
) -> Observable[_T]:
    def subscribe(
        observer: abc.ObserverBase[_T], scheduler_: abc.SchedulerBase | None = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or CurrentThreadScheduler.singleton()

        def action(_: abc.SchedulerBase, __: Any = None) -> None:
            nonlocal observer

            try:
                observer.on_next(supplier())
                observer.on_completed()
            except Exception as e:  # pylint: disable=broad-except
                observer.on_error(e)

        return _scheduler.schedule(action)

    return Observable(subscribe)


__all__ = ["return_value_", "from_callable_"]
