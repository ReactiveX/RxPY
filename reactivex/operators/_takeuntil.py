from typing import TypeVar

from reactivex import Observable, abc, from_future
from reactivex.disposable import CompositeDisposable
from reactivex.internal import curry_flip, is_future, noop
from reactivex.typing import AnyFuture

_T = TypeVar("_T")


@curry_flip
def take_until_(
    source: Observable[_T],
    other: Observable[_T] | "AnyFuture[_T]",
) -> Observable[_T]:
    """Returns the values from the source observable sequence until
    the other observable sequence produces a value.

    Examples:
        >>> source.pipe(take_until(other))
        >>> take_until(other)(source)

    Args:
        source: The source observable sequence.
        other: Observable or Future that terminates propagation.

    Returns:
        An observable sequence containing the elements of the source
        sequence up to the point the other sequence interrupted
        further propagation.
    """
    if is_future(other):
        obs: Observable[_T] = from_future(other)
    else:
        obs = other

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        stopped = False

        def on_completed(_: _T) -> None:
            nonlocal stopped
            stopped = True
            observer.on_completed()

        def on_error(error: Exception) -> None:
            nonlocal stopped
            stopped = True
            observer.on_error(error)

        other_subscription = obs.subscribe(
            on_completed, on_error, noop, scheduler=scheduler
        )
        if stopped:
            return other_subscription

        return CompositeDisposable(
            source.subscribe(observer, scheduler=scheduler),
            other_subscription,
        )

    return Observable(subscribe)


__all__ = ["take_until_"]
