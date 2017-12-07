from rx.core import Observable, AnonymousObservable
from rx.concurrency import timeout_scheduler
from rx.disposables import MultipleAssignmentDisposable
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def generate_with_relative_time(cls, initial_state, condition, iterate,
                                result_selector, time_selector):
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

    Returns the generated sequence.
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
                observer.send(result[0])

            try:
                if first[0]:
                    first[0] = False
                else:
                    state[0] = iterate(state[0])

                has_result[0] = condition(state[0])
                if has_result[0]:
                    result[0] = result_selector(state[0])
                    time[0] = time_selector(state[0])

            except Exception as e:
                observer.throw(e)
                return

            if has_result[0]:
                mad.disposable = scheduler.schedule_relative(time[0], action)
            else:
                observer.close()

        mad.disposable = scheduler.schedule_relative(0, action)
        return mad
    return AnonymousObservable(subscribe)
