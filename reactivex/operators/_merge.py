from asyncio import Future
from typing import TypeVar, Union

import reactivex
from reactivex import Observable, abc, from_future, typing
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable
from reactivex.internal import curry_flip, synchronized

_T = TypeVar("_T")


@curry_flip
def merge_(
    source: Observable[Observable[_T]],
    *sources: Observable[_T],
    max_concurrent: int | None = None,
) -> Observable[_T]:
    """Merges an observable sequence of observable sequences into
    an observable sequence, limiting the number of concurrent
    subscriptions to inner sequences. Or merges two observable
    sequences into a single observable sequence.

    Examples:
        >>> res = source.pipe(merge(max_concurrent=2))
        >>> res = merge()(source)

    Args:
        source: Source observable.
        *sources: Additional observables to merge.
        max_concurrent: Maximum number of concurrent subscriptions.

    Returns:
        The observable sequence that merges the elements of the
        inner sequences.
    """

    if max_concurrent is None:
        sources_ = tuple([source]) + sources
        return reactivex.merge(*sources_)

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ):
        active_count = [0]
        group = CompositeDisposable()
        is_stopped = [False]
        queue: list[Observable[_T]] = []

        def subscribe(xs: Observable[_T]):
            subscription = SingleAssignmentDisposable()
            group.add(subscription)

            @synchronized(source.lock)
            def on_completed():
                group.remove(subscription)
                if queue:
                    s = queue.pop(0)
                    subscribe(s)
                else:
                    active_count[0] -= 1
                    if is_stopped[0] and active_count[0] == 0:
                        observer.on_completed()

            on_next = synchronized(source.lock)(observer.on_next)
            on_error = synchronized(source.lock)(observer.on_error)
            subscription.disposable = xs.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler
            )

        def on_next(inner_source: Observable[_T]) -> None:
            assert max_concurrent
            if active_count[0] < max_concurrent:
                active_count[0] += 1
                subscribe(inner_source)
            else:
                queue.append(inner_source)

        def on_completed():
            is_stopped[0] = True
            if active_count[0] == 0:
                observer.on_completed()

        group.add(
            source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )
        )
        return group

    return Observable(subscribe)


@curry_flip
def merge_all_(source: Observable[Observable[_T]]) -> Observable[_T]:
    """Merges an observable sequence of observable sequences into an
    observable sequence.

    Examples:
        >>> res = source.pipe(merge_all())
        >>> res = merge_all()(source)

    Args:
        source: Source observable to merge.

    Returns:
        The observable sequence that merges the elements of the inner
        sequences.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ):
        group = CompositeDisposable()
        is_stopped = [False]
        m = SingleAssignmentDisposable()
        group.add(m)

        def on_next(inner_source: Union[Observable[_T], "Future[_T]"]):
            inner_subscription = SingleAssignmentDisposable()
            group.add(inner_subscription)

            inner_source = (
                from_future(inner_source)
                if isinstance(inner_source, Future)
                else inner_source
            )

            @synchronized(source.lock)
            def on_completed():
                group.remove(inner_subscription)
                if is_stopped[0] and len(group) == 1:
                    observer.on_completed()

            on_next: typing.OnNext[_T] = synchronized(source.lock)(observer.on_next)
            on_error = synchronized(source.lock)(observer.on_error)
            subscription = inner_source.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler
            )
            inner_subscription.disposable = subscription

        def on_completed():
            is_stopped[0] = True
            if len(group) == 1:
                observer.on_completed()

        m.disposable = source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )
        return group

    return Observable(subscribe)


__all__ = ["merge_", "merge_all_"]
