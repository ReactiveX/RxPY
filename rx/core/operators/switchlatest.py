from asyncio import Future
from typing import cast, Any, Callable, Union

from rx import from_future
from rx.core import Observable
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.internal.utils import is_future


def _switch_latest() -> Callable[[Observable], Observable]:
    def switch_latest(source: Observable) -> Observable:
        """Partially applied switch_latest operator.

        Transforms an observable sequence of observable sequences into
        an observable sequence producing values only from the most
        recent observable sequence.

        Returns:
            An observable sequence that at any point in time produces
            the elements of the most recent inner observable sequence
            that has been received.
        """

        def subscribe(observer, scheduler=None):
            inner_subscription = SerialDisposable()
            has_latest = [False]
            is_stopped = [False]
            latest = [0]

            def on_next(inner_source: Union[Observable, Future]):
                nonlocal source

                d = SingleAssignmentDisposable()
                with source.lock:
                    latest[0] += 1
                    _id = latest[0]
                has_latest[0] = True
                inner_subscription.disposable = d

                # Check if Future or Observable
                if is_future(inner_source):
                    obs = from_future(cast(Future, inner_source))
                else:
                    obs = cast(Observable, inner_source)

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

                d.disposable = obs.subscribe_(on_next, on_error, on_completed, scheduler=scheduler)

            def on_completed() -> None:
                is_stopped[0] = True
                if not has_latest[0]:
                    observer.on_completed()

            subscription = source.subscribe_(on_next, observer.on_error, on_completed, scheduler=scheduler)
            return CompositeDisposable(subscription, inner_subscription)
        return Observable(subscribe)
    return switch_latest
