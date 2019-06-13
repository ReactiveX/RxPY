from asyncio import Future
from typing import cast, Callable, Optional, Union

from rx import from_future
from rx.core import Observable, typing
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.utils import is_future


def _skip_until(other: Union[Observable, Future]
                ) -> Callable[[Observable], Observable]:
    """Returns the values from the source observable sequence only after
    the other observable sequence produces a value.

    Args:
        other: The observable sequence that triggers propagation of
            elements of the source sequence.

    Returns:
        An observable sequence containing the elements of the source
    sequence starting from the point the other sequence triggered
    propagation.
    """

    if is_future(other):
        obs = from_future(cast(Future, other))
    else:
        obs = cast(Observable, other)

    def skip_until(source: Observable) -> Observable:
        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            is_open = [False]

            def on_next(left):
                if is_open[0]:
                    observer.on_next(left)

            def on_completed():
                if is_open[0]:
                    observer.on_completed()

            subs = source.subscribe(
                on_next,
                observer.on_error,
                on_completed,
                scheduler=scheduler
            )
            subscriptions = CompositeDisposable(subs)

            right_subscription = SingleAssignmentDisposable()
            subscriptions.add(right_subscription)

            def on_next2(x):
                is_open[0] = True
                right_subscription.dispose()

            def on_completed2():
                right_subscription.dispose()

            right_subscription.disposable = obs.subscribe(
                on_next2,
                observer.on_error,
                on_completed2,
                scheduler=scheduler
            )

            return subscriptions
        return Observable(subscribe_observer=subscribe_observer)
    return skip_until
