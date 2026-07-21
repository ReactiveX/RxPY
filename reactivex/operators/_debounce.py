from collections.abc import Callable
from typing import Any, TypeVar, cast

from reactivex import Observable, abc, typing
from reactivex.disposable import (
    CompositeDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import curry_flip
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@curry_flip
def debounce_(
    source: Observable[_T],
    duetime: typing.RelativeTime,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[_T]:
    """Ignores values from an observable sequence which are followed by
    another value before duetime.

    Examples:
        >>> res = source.pipe(debounce(0.5))
        >>> res = debounce(0.5)(source)

    Args:
        source: Source observable to debounce.
        duetime: Duration to wait before emitting.
        scheduler: Scheduler to use.

    Returns:
        The debounced observable sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler_: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
        cancelable = SerialDisposable()
        has_value = [False]
        value: list[_T] = [cast(_T, None)]
        _id: list[int] = [0]

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


@curry_flip
def throttle_with_mapper_(
    source: Observable[_T],
    throttle_duration_mapper: Callable[[Any], Observable[Any]],
) -> Observable[_T]:
    """Ignores values from an observable sequence which are followed by
    another value within a computed throttle duration.

    Examples:
        >>> res = source.pipe(throttle_with_mapper(lambda x: timer(x)))
        >>> res = throttle_with_mapper(lambda x: timer(x))(source)

    Args:
        source: The observable source to throttle.
        throttle_duration_mapper: Function to compute throttle duration.

    Returns:
        The throttled observable sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
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


__all__ = ["debounce_", "throttle_with_mapper_"]
