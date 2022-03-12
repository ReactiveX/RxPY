from typing import Any, Callable, Optional, TypeVar, cast

from reactivex import Observable, abc
from reactivex.disposable import MultipleAssignmentDisposable
from reactivex.scheduler import TimeoutScheduler
from reactivex.typing import Mapper, Predicate, RelativeTime

_TState = TypeVar("_TState")


def generate_with_relative_time_(
    initial_state: _TState,
    condition: Predicate[_TState],
    iterate: Mapper[_TState, _TState],
    time_mapper: Callable[[_TState], RelativeTime],
) -> Observable[_TState]:
    """Generates an observable sequence by iterating a state from an
    initial state until the condition fails.

    Example:
        res = source.generate_with_relative_time(
            0, lambda x: True, lambda x: x + 1, lambda x: 0.5
        )

    Args:
        initial_state: Initial state.
        condition: Condition to terminate generation (upon returning
            false).
        iterate: Iteration step function.
        time_mapper: Time mapper function to control the speed of
            values being produced each iteration, returning relative
            times, i.e. either floats denoting seconds or instances of
            timedelta.

    Returns:
        The generated sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_TState],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        scheduler = scheduler or TimeoutScheduler.singleton()
        mad = MultipleAssignmentDisposable()
        state = initial_state
        has_result = False
        result: _TState = cast(_TState, None)
        first = True
        time: Optional[RelativeTime] = None

        def action(scheduler: abc.SchedulerBase, _: Any) -> None:
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
                assert time
                mad.disposable = scheduler.schedule_relative(time, action)
            else:
                observer.on_completed()

        mad.disposable = scheduler.schedule_relative(0, action)
        return mad

    return Observable(subscribe)


__all__ = ["generate_with_relative_time_"]
