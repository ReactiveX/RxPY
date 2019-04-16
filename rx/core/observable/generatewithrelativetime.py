from rx.core import Observable
from rx.concurrency import timeout_scheduler
from rx.disposable import MultipleAssignmentDisposable


def _generate_with_relative_time(initial_state, condition, iterate, time_mapper) -> Observable:
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
        scheduler = scheduler or timeout_scheduler
        mad = MultipleAssignmentDisposable()
        state = [initial_state]
        has_result = [False]
        result = [None]
        first = [True]
        time = [None]

        def action(scheduler, _):
            if has_result[0]:
                observer.on_next(result[0])

            try:
                if first[0]:
                    first[0] = False
                else:
                    state[0] = iterate(state[0])

                has_result[0] = condition(state[0])
                if has_result[0]:
                    result[0] = state[0]
                    time[0] = time_mapper(state[0])

            except Exception as e:
                observer.on_error(e)
                return

            if has_result[0]:
                mad.disposable = scheduler.schedule_relative(time[0], action)
            else:
                observer.on_completed()

        mad.disposable = scheduler.schedule_relative(0, action)
        return mad
    return Observable(subscribe)
