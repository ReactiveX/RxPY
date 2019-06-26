from typing import Callable, Optional

from rx import operators as ops
from rx.core import Observable
from rx.core.typing import Scheduler
from rx.scheduler import TimeoutScheduler
from rx.subject import AsyncSubject


def _to_async(func: Callable,
              scheduler: Optional[Scheduler] = None
              ) -> Callable:
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

    _scheduler = scheduler or TimeoutScheduler.singleton()

    def wrapper(*args) -> Observable:
        subject = AsyncSubject()

        def action(scheduler, state):
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
