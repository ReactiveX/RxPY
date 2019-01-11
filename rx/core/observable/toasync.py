from typing import Callable

from rx import operators as ops
from rx.core import Observable
from rx.concurrency import timeout_scheduler
from rx.subjects import AsyncSubject


def _to_async(func: Callable, scheduler=None) -> Callable:
    """Converts the function into an asynchronous function. Each
    invocation of the resulting asynchronous function causes an
    invocation of the original synchronous function on the specified
    scheduler.

    Examples:
        res = rx.to_async(lambda x, y: x + y)(4, 3)
        res = rx.to_async(lambda x, y: x + y, Scheduler.timeout)(4, 3)
        res = rx.to_async(lambda x: log.debug(x), Scheduler.timeout)('hello')

    Args:
        func: Function to convert to an asynchronous function.
        scheduler: [Optional] Scheduler to run the function on. If not
            specified, defaults to Scheduler.timeout.

    Returns:
        Aynchronous function.
    """

    scheduler = scheduler or timeout_scheduler

    def wrapper(*args) -> Observable:
        subject = AsyncSubject()

        def action(scheduler, state):
            try:
                result = func(*args)
            except Exception as ex:
                subject.on_error(ex)
                return

            subject.on_next(result)
            subject.on_completed()

        scheduler.schedule(action)
        return subject.pipe(ops.as_observable())
    return wrapper
