from asyncio import Future
from typing import TypeVar

from reactivex import Observable, abc, from_future
from reactivex.disposable import CompositeDisposable
from reactivex.internal import curry_flip, noop

_T = TypeVar("_T")


@curry_flip
def take_until_(
    source: Observable[_T],
    other: Observable[_T] | Future[_T],
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
    if isinstance(other, Future):
        obs: Observable[_T] = from_future(other)
    else:
        obs = other

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        def on_completed(_: _T) -> None:
            observer.on_completed()

        return CompositeDisposable(
            source.subscribe(observer, scheduler=scheduler),
            obs.subscribe(on_completed, observer.on_error, noop, scheduler=scheduler),
        )

    return Observable(subscribe)


__all__ = ["take_until_"]
