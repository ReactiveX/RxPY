from rx.core import Observable
from rx.concurrency import current_thread_scheduler
from rx.disposable import MultipleAssignmentDisposable


def _generate(initial_state, condition, iterate) -> Observable:
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
                    result = state[0]

            except Exception as exception:  # pylint: disable=broad-except
                observer.on_error(exception)
                return

            if has_result:
                observer.on_next(result)
                mad.disposable = scheduler.schedule(action)
            else:
                observer.on_completed()

        mad.disposable = scheduler.schedule(action)
        return mad
    return Observable(subscribe)
