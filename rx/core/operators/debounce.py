from typing import Any, Callable, List, Optional, TypeVar, cast

from rx.core import Observable, abc, typing
from rx.disposable import (
    CompositeDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from rx.scheduler import TimeoutScheduler

_T = TypeVar("_T")


def _debounce(
    duetime: typing.RelativeTime, scheduler: abc.SchedulerBase
) -> Callable[[Observable[_T]], Observable[_T]]:
    def debounce(source: Observable[_T]) -> Observable[_T]:
        """Ignores values from an observable sequence which are followed by
        another value before duetime.

        Example:
            >>> res = debounce(source)

        Args:
            source: Source observable to debounce.

        Returns:
            An operator function that takes the source observable and
            returns the debounced observable sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
            cancelable = SerialDisposable()
            has_value = [False]
            value: List[_T] = [cast(_T, None)]
            _id: List[int] = [0]

            def on_next(x: _T) -> None:
                has_value[0] = True
                value[0] = x
                _id[0] += 1
                current_id = _id[0]
                d = SingleAssignmentDisposable()
                cancelable.disposable = d

                def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
                    if has_value[0] and _id[0] == current_id:
                        observer.on_next(value[0])
                    has_value[0] = False

                d.disposable = _scheduler.schedule_relative(duetime, action)

            def on_error(exception: Exception) -> None:
                cancelable.dispose()
                observer.on_error(exception)
                has_value[0] = False
                _id[0] += 1

            def on_completed() -> None:
                cancelable.dispose()
                if has_value[0]:
                    observer.on_next(value[0])

                observer.on_completed()
                has_value[0] = False
                _id[0] += 1

            subscription = source.subscribe_(
                on_next, on_error, on_completed, scheduler=scheduler_
            )
            return CompositeDisposable(subscription, cancelable)

        return Observable(subscribe)

    return debounce


def _throttle_with_mapper(
    throttle_duration_mapper: Callable[[Any], Observable[_T]]
) -> Callable[[Observable[_T]], Observable[_T]]:
    def throttle_with_mapper(source: Observable[_T]) -> Observable[_T]:
        """Partially applied throttle_with_mapper operator.

        Ignores values from an observable sequence which are followed by
        another value within a computed throttle duration.

        Example:
            >>> obs = throttle_with_mapper(source)

        Args:
            source: The observable source to throttle.

        Returns:
            The throttled observable sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            cancelable = SerialDisposable()
            has_value = [False]
            value = [None]
            _id = [0]

            def on_next(x):
                throttle = None
                try:
                    throttle = throttle_duration_mapper(x)
                except Exception as e:  # pylint: disable=broad-except
                    observer.on_error(e)
                    return

                has_value[0] = True
                value[0] = x
                _id[0] += 1
                current_id = _id[0]
                d = SingleAssignmentDisposable()
                cancelable.disposable = d

                def on_next(x: _T) -> None:
                    if has_value[0] and _id[0] == current_id:
                        observer.on_next(value[0])

                    has_value[0] = False
                    d.dispose()

                def on_completed() -> None:
                    if has_value[0] and _id[0] == current_id:
                        observer.on_next(value[0])

                    has_value[0] = False
                    d.dispose()

                d.disposable = throttle.subscribe_(
                    on_next, observer.on_error, on_completed, scheduler=scheduler
                )

            def on_error(e: Exception) -> None:
                cancelable.dispose()
                observer.on_error(e)
                has_value[0] = False
                _id[0] += 1

            def on_completed() -> None:
                cancelable.dispose()
                if has_value[0]:
                    observer.on_next(value[0])

                observer.on_completed()
                has_value[0] = False
                _id[0] += 1

            subscription = source.subscribe_(
                on_next, on_error, on_completed, scheduler=scheduler
            )
            return CompositeDisposable(subscription, cancelable)

        return Observable(subscribe)

    return throttle_with_mapper


__all__ = ["_debounce", "_throttle_with_mapper"]
