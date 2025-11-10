from asyncio import Future
from typing import Any, TypeVar, Union

from reactivex import Observable, abc, from_future
from reactivex.disposable import (
    CompositeDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def switch_latest_(
    source: Observable[Union[Observable[_T], "Future[_T]"]],
) -> Observable[_T]:
    """Transforms an observable sequence of observable sequences into
    an observable sequence producing values only from the most
    recent observable sequence.

    Examples:
        >>> res = source.pipe(switch_latest())
        >>> res = switch_latest()(source)

    Args:
        source: Source observable of observables.

    Returns:
        An observable sequence that at any point in time produces
        the elements of the most recent inner observable sequence
        that has been received.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        inner_subscription = SerialDisposable()
        has_latest = [False]
        is_stopped = [False]
        latest = [0]

        def on_next(inner_source: Union[Observable[_T], "Future[_T]"]) -> None:
            nonlocal source

            d = SingleAssignmentDisposable()
            with source.lock:
                latest[0] += 1
                _id = latest[0]
            has_latest[0] = True
            inner_subscription.disposable = d

            # Check if Future or Observable
            if isinstance(inner_source, Future):
                obs = from_future(inner_source)
            else:
                obs = inner_source

            def on_next(x: Any) -> None:
                if latest[0] == _id:
                    observer.on_next(x)

            def on_error(e: Exception) -> None:
                if latest[0] == _id:
                    observer.on_error(e)

            def on_completed() -> None:
                if latest[0] == _id:
                    has_latest[0] = False
                    if is_stopped[0]:
                        observer.on_completed()

            d.disposable = obs.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler
            )

        def on_completed() -> None:
            is_stopped[0] = True
            if not has_latest[0]:
                observer.on_completed()

        subscription = source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )
        return CompositeDisposable(subscription, inner_subscription)

    return Observable(subscribe)


__all__ = ["switch_latest_"]
