from asyncio import Future
from typing import Any, TypeVar, Union

from reactivex import Observable, abc, from_future
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def skip_until_(
    source: Observable[_T],
    other: Union[Observable[Any], "Future[Any]"],
) -> Observable[_T]:
    """Returns the values from the source observable sequence only after
    the other observable sequence produces a value.

    Examples:
        >>> source.pipe(skip_until(other))
        >>> skip_until(other)(source)

    Args:
        source: Source observable to skip elements from.
        other: The observable sequence that triggers propagation of
            elements of the source sequence.

    Returns:
        An observable sequence containing the elements of the source
        sequence starting from the point the other sequence triggered
        propagation.
    """

    if isinstance(other, Future):
        obs: Observable[Any] = from_future(other)
    else:
        obs = other

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ):
        is_open = [False]

        def on_next(left: _T) -> None:
            if is_open[0]:
                observer.on_next(left)

        def on_completed() -> None:
            if is_open[0]:
                observer.on_completed()

        subs = source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )
        subscriptions = CompositeDisposable(subs)

        right_subscription = SingleAssignmentDisposable()
        subscriptions.add(right_subscription)

        def on_next2(x: Any) -> None:
            is_open[0] = True
            right_subscription.dispose()

        def on_completed2():
            right_subscription.dispose()

        right_subscription.disposable = obs.subscribe(
            on_next2, observer.on_error, on_completed2, scheduler=scheduler
        )

        return subscriptions

    return Observable(subscribe)


__all__ = ["skip_until_"]
