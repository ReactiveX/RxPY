from typing import Any, Optional, TypeVar, cast

from reactivex import Observable, abc, typing
from reactivex.disposable import MultipleAssignmentDisposable
from reactivex.scheduler import CurrentThreadScheduler

_TState = TypeVar("_TState")


def generate_(
    initial_state: _TState,
    condition: typing.Predicate[_TState],
    iterate: typing.Mapper[_TState, _TState],
) -> Observable[_TState]:
    def subscribe(
        observer: abc.ObserverBase[_TState],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        scheduler = scheduler or CurrentThreadScheduler.singleton()
        first = True
        state = initial_state
        mad = MultipleAssignmentDisposable()

        def action(scheduler: abc.SchedulerBase, state1: Any = None) -> None:
            nonlocal first
            nonlocal state

            has_result = False
            result: _TState = cast(_TState, None)

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

    return Observable(subscribe)


__all__ = ["generate_"]
