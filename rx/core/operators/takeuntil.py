from asyncio import Future
from typing import Callable, Optional, Union, cast, TypeVar

from rx import from_future
from rx.core import Observable, abc
from rx.disposable import CompositeDisposable
from rx.internal import noop
from rx.internal.utils import is_future

_T = TypeVar("_T")


def _take_until(
    other: Union[Observable[_T], "Future[_T]"]
) -> Callable[[Observable[_T]], Observable[_T]]:
    if is_future(other):
        obs: Observable[_T] = from_future(other)
    else:
        obs = cast(Observable[_T], other)

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
                source.subscribe(observer),
                obs.subscribe_(on_completed, observer.on_error, noop, scheduler),
            )

        return Observable(subscribe)

    return take_until


__all__ = ["_take_until"]
