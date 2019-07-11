from typing import Any, Callable

from rx.core import Observable
from rx.core.typing import Predicate, Mapper, RelativeTime
from rx.scheduler import TimeoutScheduler
from rx.disposable import MultipleAssignmentDisposable


def _generate_with_relative_time(initial_state: Any,
                                 condition: Predicate,
                                 iterate: Mapper,
                                 time_mapper: Callable[[Any], RelativeTime]
                                 ) -> Observable:
    """Generates an observable sequence by iterating a state from an
    initial state until the condition fails.

    Example:
        res = source.generate_with_relative_time(0, lambda x: True, lambda x: x + 1, lambda x: 0.5)

    Args:
        initial_state: Initial state.
        condition: Condition to terminate generation (upon returning
            false).
        iterate: Iteration step function.
        time_mapper: Time mapper function to control the speed of
            values being produced each iteration, returning relative times, i.e.
            either floats denoting seconds or instances of timedelta.

    Returns:
        The generated sequence.
    """

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or TimeoutScheduler.singleton()
        mad = MultipleAssignmentDisposable()
        state = initial_state
        has_result = False
        result = None
        first = True
        time = None

        def action(scheduler, _):
            nonlocal state
            nonlocal has_result
            nonlocal result
            nonlocal first
            nonlocal time

            if has_result:
                observer.on_next(result)

            try:
                if first:
                    first = False
                else:
                    state = iterate(state)

                has_result = condition(state)

                if has_result:
                    result = state
                    time = time_mapper(state)

            except Exception as e:  # pylint: disable=broad-except
                observer.on_error(e)
                return

            if has_result:
                mad.disposable = scheduler.schedule_relative(time, action)
            else:
                observer.on_completed()

        mad.disposable = scheduler.schedule_relative(0, action)
        return mad
    return Observable(subscribe)
