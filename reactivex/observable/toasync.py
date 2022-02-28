from typing import Any, Callable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex import operators as ops
from reactivex.scheduler import TimeoutScheduler
from reactivex.subject import AsyncSubject

_T = TypeVar("_T")


def to_async_(
    func: Callable[..., _T], scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[..., Observable[_T]]:
    """Converts the function into an asynchronous function. Each
    invocation of the resulting asynchronous function causes an
    invocation of the original synchronous function on the specified
    scheduler.

    Examples:
        res = reactivex.to_async(lambda x, y: x + y)(4, 3)
        res = reactivex.to_async(lambda x, y: x + y, Scheduler.timeout)(4, 3)
        res = reactivex.to_async(lambda x: log.debug(x), Scheduler.timeout)('hello')

    Args:
        func: Function to convert to an asynchronous function.
        scheduler: [Optional] Scheduler to run the function on. If not
            specified, defaults to Scheduler.timeout.

    Returns:
        Aynchronous function.
    """

    _scheduler = scheduler or TimeoutScheduler.singleton()

    def wrapper(*args: Any) -> Observable[_T]:
        subject: AsyncSubject[_T] = AsyncSubject()

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            try:
                result = func(*args)
            except Exception as ex:  # pylint: disable=broad-except
                subject.on_error(ex)
                return

            subject.on_next(result)
            subject.on_completed()

        _scheduler.schedule(action)
        return subject.pipe(ops.as_observable())

    return wrapper


__all__ = ["to_async_"]
