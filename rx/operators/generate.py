from rx.core import ObservableBase, AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.disposables import MultipleAssignmentDisposable


def generate(initial_state, condition, iterate, result_mapper) -> ObservableBase:
    """Generates an observable sequence by running a state-driven loop
    producing the sequence's elements, using the specified scheduler to
    send out observer messages.

    1 - res = rx.Observable.generate(0,
        lambda x: x < 10,
        lambda x: x + 1,
        lambda x: x)

    Keyword arguments:
    initial_state -- Initial state.
    condition -- Condition to terminate generation (upon returning False).
    iterate -- Iteration step function.
    result_mapper -- Selector function for results produced in the
        sequence.

    Returns the generated sequence.
    """

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler
        first = [True]
        state = [initial_state]
        mad = MultipleAssignmentDisposable()

        def action(scheduler, state1=None):
            has_result = False
            result = None

            try:
                if first[0]:
                    first[0] = False
                else:
                    state[0] = iterate(state[0])

                has_result = condition(state[0])
                if has_result:
                    result = result_mapper(state[0])

            except Exception as exception:
                observer.on_error(exception)
                return

            if has_result:
                observer.on_next(result)
                mad.disposable = scheduler.schedule(action)
            else:
                observer.on_completed()

        mad.disposable = scheduler.schedule(action)
        return mad
    return AnonymousObservable(subscribe)
