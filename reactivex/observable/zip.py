from asyncio import Future
from threading import RLock
from typing import Any, List, Optional, Tuple

from reactivex import Observable, abc, from_future
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable
from reactivex.internal import synchronized


def zip_(*args: Observable[Any]) -> Observable[Tuple[Any, ...]]:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    Example:
        >>> res = zip(obs1, obs2)

    Args:
        args: Observable sources to zip.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources as tuple.
    """

    sources = list(args)

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> CompositeDisposable:
        n = len(sources)
        queues: List[List[Any]] = [[] for _ in range(n)]
        lock = RLock()
        is_completed = [False] * n

        @synchronized(lock)
        def next_(i: int) -> None:
            if all(len(q) for q in queues):
                try:
                    queued_values = [x.pop(0) for x in queues]
                    res = tuple(queued_values)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return

                observer.on_next(res)

                # after sending the zipped values, complete the observer if at least one
                # upstream observable is completed and its queue has length zero
                if any(
                    (
                        done
                        for queue, done in zip(queues, is_completed)
                        if len(queue) == 0
                    )
                ):
                    observer.on_completed()

        def completed(i: int) -> None:
            is_completed[i] = True
            if len(queues[i]) == 0:
                observer.on_completed()

        subscriptions: List[Optional[abc.DisposableBase]] = [None] * n

        def func(i: int) -> None:
            source: Observable[Any] = sources[i]
            if isinstance(source, Future):
                source = from_future(source)

            sad = SingleAssignmentDisposable()

            def on_next(x: Any) -> None:
                queues[i].append(x)
                next_(i)

            sad.disposable = source.subscribe(
                on_next, observer.on_error, lambda: completed(i), scheduler=scheduler
            )
            subscriptions[i] = sad

        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)

    return Observable(subscribe)


__all__ = ["zip_"]
