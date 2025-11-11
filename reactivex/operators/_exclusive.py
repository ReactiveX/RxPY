from asyncio import Future
from typing import TypeVar, Union

import reactivex
from reactivex import Observable, abc
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def exclusive_(source: Observable[Observable[_T]]) -> Observable[_T]:
    """Performs a exclusive waiting for the first to finish before
    subscribing to another observable. Observables that come in between
    subscriptions will be dropped on the floor.

    Examples:
        >>> res = source.pipe(exclusive())
        >>> res = exclusive()(source)

    Args:
        source: Source observable of observables.

    Returns:
        An exclusive observable with only the results that
        happen when subscribed.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        has_current = [False]
        is_stopped = [False]
        m = SingleAssignmentDisposable()
        g = CompositeDisposable()

        g.add(m)

        def on_next(inner_source: Union[Observable[_T], "Future[_T]"]) -> None:
            if not has_current[0]:
                has_current[0] = True

                inner_source = (
                    reactivex.from_future(inner_source)
                    if isinstance(inner_source, Future)
                    else inner_source
                )

                inner_subscription = SingleAssignmentDisposable()
                g.add(inner_subscription)

                def on_completed_inner():
                    g.remove(inner_subscription)
                    has_current[0] = False
                    if is_stopped[0] and len(g) == 1:
                        observer.on_completed()

                inner_subscription.disposable = inner_source.subscribe(
                    observer.on_next,
                    observer.on_error,
                    on_completed_inner,
                    scheduler=scheduler,
                )

        def on_completed() -> None:
            is_stopped[0] = True
            if not has_current[0] and len(g) == 1:
                observer.on_completed()

        m.disposable = source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )
        return g

    return Observable(subscribe)


__all__ = ["exclusive_"]
