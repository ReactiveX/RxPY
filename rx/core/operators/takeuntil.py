from asyncio import Future
from typing import cast, Callable, Union

from rx import from_future
from rx.internal import noop
from rx.core import Observable
from rx.disposable import CompositeDisposable
from rx.internal.utils import is_future


def _take_until(other: Union[Observable, Future]) -> Callable[[Observable], Observable]:
    if is_future(other):
        obs = from_future(cast(Future, other))
    else:
        obs = cast(Observable, other)

    def take_until(source: Observable) -> Observable:
        """Returns the values from the source observable sequence until
        the other observable sequence produces a value.

        Args:
            source: The source observable sequence.

        Returns:
            An observable sequence containing the elements of the source
            sequence up to the point the other sequence interrupted
            further propagation.
        """

        def subscribe(observer, scheduler=None):

            def on_completed(_):
                observer.on_completed()

            return CompositeDisposable(
                source.subscribe(observer),
                obs.subscribe_(on_completed, observer.on_error, noop, scheduler)
            )
        return Observable(subscribe)
    return take_until
