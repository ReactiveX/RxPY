from typing import Any, Callable, List, Optional, TypeVar, cast

from reactivex import Observable, abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


def debounce_(
    duetime: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase]
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

            subscription = source.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler_
            )
            return CompositeDisposable(subscription, cancelable)

        return Observable(subscribe)

    return debounce


def throttle_with_mapper_(
    throttle_duration_mapper: Callable[[Any], Observable[Any]]
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
            has_value: bool = False
            value: _T = cast(_T, None)
            _id = [0]

            def on_next(x: _T) -> None:
                nonlocal value, has_value

                throttle = None
                try:
                    throttle = throttle_duration_mapper(x)
                except Exception as e:  # pylint: disable=broad-except
                    observer.on_error(e)
                    return

                has_value = True
                value = x
                _id[0] += 1
                current_id = _id[0]
                d = SingleAssignmentDisposable()
                cancelable.disposable = d

                def on_next(x: Any) -> None:
                    nonlocal has_value
                    if has_value and _id[0] == current_id:
                        observer.on_next(value)

                    has_value = False
                    d.dispose()

                def on_completed() -> None:
                    nonlocal has_value
                    if has_value and _id[0] == current_id:
                        observer.on_next(value)

                    has_value = False
                    d.dispose()

                d.disposable = throttle.subscribe(
                    on_next, observer.on_error, on_completed, scheduler=scheduler
                )

            def on_error(e: Exception) -> None:
                nonlocal has_value
                cancelable.dispose()
                observer.on_error(e)
                has_value = False
                _id[0] += 1

            def on_completed() -> None:
                nonlocal has_value
                cancelable.dispose()
                if has_value:
                    observer.on_next(value)

                observer.on_completed()
                has_value = False
                _id[0] += 1

            subscription = source.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler
            )
            return CompositeDisposable(subscription, cancelable)

        return Observable(subscribe)

    return throttle_with_mapper


__all__ = ["debounce_", "throttle_with_mapper_"]
