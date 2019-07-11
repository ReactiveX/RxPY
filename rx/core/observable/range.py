from sys import maxsize
from typing import Optional

from rx.core import typing
from rx.core import Observable
from rx.scheduler import CurrentThreadScheduler
from rx.disposable import MultipleAssignmentDisposable


def _range(start: int,
           stop: Optional[int] = None,
           step: Optional[int] = None,
           scheduler: Optional[typing.Scheduler] = None
           ) -> Observable:
    """Generates an observable sequence of integral numbers within a
    specified range, using the specified scheduler to send out observer
    messages.

    Examples:
        >>> res = range(10)
        >>> res = range(0, 10)
        >>> res = range(0, 10, 1)

    Args:
        start: The value of the first integer in the sequence.
        count: The number of sequential integers to generate.
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

    def subscribe(observer, scheduler_: typing.Scheduler = None):
        nonlocal range_t

        _scheduler = scheduler or scheduler_ or CurrentThreadScheduler.singleton()
        sd = MultipleAssignmentDisposable()

        def action(scheduler, iterator):
            try:
                observer.on_next(next(iterator))
                sd.disposable = _scheduler.schedule(action, state=iterator)
            except StopIteration:
                observer.on_completed()

        sd.disposable = _scheduler.schedule(action, iter(range_t))
        return sd
    return Observable(subscribe)
