from asyncio import Future
from typing import Callable, Optional, TypeVar, Union

from reactivex import Observable, abc, from_future
from reactivex.disposable import CompositeDisposable
from reactivex.internal import noop

_T = TypeVar("_T")


def take_until_(
    other: Union[Observable[_T], "Future[_T]"]
) -> Callable[[Observable[_T]], Observable[_T]]:
    if isinstance(other, Future):
        obs: Observable[_T] = from_future(other)
    else:
        obs = other

    def take_until(source: Observable[_T]) -> Observable[_T]:
        """Returns the values from the source observable sequence until
        the other observable sequence produces a value.

        Args:
            source: The source observable sequence.

        Returns:
            An observable sequence containing the elements of the source
            sequence up to the point the other sequence interrupted
            further propagation.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            def on_completed(_: _T) -> None:
                observer.on_completed()

            return CompositeDisposable(
                source.subscribe(observer, scheduler=scheduler),
                obs.subscribe(
                    on_completed, observer.on_error, noop, scheduler=scheduler
                ),
            )

        return Observable(subscribe)

    return take_until


__all__ = ["take_until_"]
