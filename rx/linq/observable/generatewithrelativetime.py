from rx.core import Observable, AnonymousObservable
from rx.concurrency import timeout_scheduler
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def generate_with_relative_time(cls, initial_state, condition, iterate,
                                result_selector, time_selector,
                                scheduler=None):
    """Generates an observable sequence by iterating a state from an
    initial state until the condition fails.

    res = source.generate_with_relative_time(0,
        lambda x: True,
        lambda x: x + 1,
        lambda x: x,
        lambda x: 500)

    initial_state -- Initial state.
    condition -- Condition to terminate generation (upon returning false).
    iterate -- Iteration step function.
    result_selector -- Selector function for results produced in the
        sequence.
    time_selector -- Time selector function to control the speed of values
        being produced each iteration, returning integer values denoting
        milliseconds.
    scheduler -- [Optional] Scheduler on which to run the generator loop.
        If not specified, the timeout scheduler is used.

    Returns the generated sequence.
    """

    scheduler = scheduler or timeout_scheduler

    def subscribe(observer):
        state = [initial_state]
        has_result = [False]
        result = [None]
        first = [True]
        time = None

        def action(this):
            if has_result[0]:
                observer.on_next(result[0])

            try:
                if first[0]:
                    first[0] = False
                else:
                    state[0] = iterate(state[0])

                has_result[0] = condition(state[0])
                if has_result[0]:
                    result[0] = result_selector(state[0])
                    time = time_selector(state[0])

            except Exception as e:
                observer.on_error(e)
                return

            if has_result[0]:
                this(time)
            else:
                observer.on_completed()

        return scheduler.schedule_recursive_with_relative(0, action)
    return AnonymousObservable(subscribe)

