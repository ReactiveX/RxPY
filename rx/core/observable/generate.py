from typing import Any, Optional

from rx.core import Observable, typing
from rx.core.typing import Mapper, Predicate
from rx.scheduler import CurrentThreadScheduler
from rx.disposable import MultipleAssignmentDisposable


def _generate(initial_state: Any,
              condition: Predicate,
              iterate: Mapper
              ) -> Observable:

    def subscribe_observer(observer: typing.Observer,
                           scheduler: Optional[typing.Scheduler] = None
                           ) -> typing.Disposable:
        scheduler = scheduler or CurrentThreadScheduler.singleton()
        first = True
        state = initial_state
        mad = MultipleAssignmentDisposable()

        def action(scheduler, state1=None):
            nonlocal first
            nonlocal state

            has_result = False
            result = None

            try:
                if first:
                    first = False
                else:
                    state = iterate(state)

                has_result = condition(state)
                if has_result:
                    result = state

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
    return Observable(subscribe_observer=subscribe_observer)
