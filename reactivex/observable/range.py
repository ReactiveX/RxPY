from sys import maxsize
from typing import Iterator, Optional

from reactivex import Observable, abc
from reactivex.disposable import MultipleAssignmentDisposable
from reactivex.scheduler import CurrentThreadScheduler


def range_(
    start: int,
    stop: Optional[int] = None,
    step: Optional[int] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Observable[int]:
    """Generates an observable sequence of integral numbers within a
    specified range, using the specified scheduler to send out observer
    messages.

    Examples:
        >>> res = range(10)
        >>> res = range(0, 10)
        >>> res = range(0, 10, 1)

    Args:
        start: The value of the first integer in the sequence.
        stop: [Optional] Generate number up to (exclusive) the stop
            value. Default is `sys.maxsize`.
        step: [Optional] The step to be used (default is 1).
        scheduler: The scheduler to schedule the values on.

    Returns:
        An observable sequence that contains a range of sequential
        integral numbers.
    """

    _stop: int = maxsize if stop is None else stop
    _step: int = 1 if step is None else step

    if step is None and stop is None:
        range_t = range(start)
    elif step is None:
        range_t = range(start, _stop)
    else:
        range_t = range(start, _stop, _step)

    def subscribe(
        observer: abc.ObserverBase[int], scheduler_: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        nonlocal range_t

        _scheduler = scheduler or scheduler_ or CurrentThreadScheduler.singleton()
        sd = MultipleAssignmentDisposable()

        def action(
            scheduler: abc.SchedulerBase, iterator: Optional[Iterator[int]]
        ) -> None:
            try:
                assert iterator
                observer.on_next(next(iterator))
                sd.disposable = _scheduler.schedule(action, state=iterator)
            except StopIteration:
                observer.on_completed()

        sd.disposable = _scheduler.schedule(action, iter(range_t))
        return sd

    return Observable(subscribe)


__all__ = ["range_"]
