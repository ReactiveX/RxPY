from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc, to_async

_T = TypeVar("_T")


def start_(
    func: Callable[[], _T], scheduler: Optional[abc.SchedulerBase] = None
) -> Observable[_T]:
    """Invokes the specified function asynchronously on the specified
    scheduler, surfacing the result through an observable sequence.

    Example:
        >>> res = reactivex.start(lambda: pprint('hello'))
        >>> res = reactivex.start(lambda: pprint('hello'), rx.Scheduler.timeout)

    Args:
        func: Function to run asynchronously.
        scheduler: [Optional] Scheduler to run the function on. If
            not specified, defaults to Scheduler.timeout.

    Remarks:
        The function is called immediately, not during the subscription
        of the resulting sequence. Multiple subscriptions to the
        resulting sequence can observe the function's result.

    Returns:
        An observable sequence exposing the function's result value,
        or an exception.
    """

    return to_async(func, scheduler)()


__all__ = ["start_"]
