from asyncio import Future
from threading import RLock
from typing import Any, Callable, List, Optional, Tuple

from reactivex import Observable, abc, from_future
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable
from reactivex.internal import synchronized


def combine_throttle_(*args: Observable[Any]) -> Observable[Tuple[Any, ...]]:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever all of the observable sequences
    have produced an element at a corresponding index.

    Example:
        >>> res = combine_throttle(source)

    Args:
        args: Observable sources to combine_throttle.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources as a tuple.
    """

    n = len(args)

    sources = list(args)

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> CompositeDisposable:

        flags = (1 << (n - 1)) & 0  # Reserve n zero bits.
        full_mask = 1 << (n - 1)
        full_mask |= full_mask - 1  # Create mask with n 1 bits.
        lock = RLock()

        results: List[None] = [None] * n

        def create_on_next(i: int) -> Callable[[Any], None]:
            @synchronized(lock)
            def on_next(item: Any) -> None:
                nonlocal flags
                results[i] = item
                flags |= 1 << i
                if flags == full_mask:
                    flags = 0
                    observer.on_next(tuple(results))

            return on_next

        subscriptions: List[abc.DisposableBase] = []

        for i in range(len(sources)):
            source: Observable[Any] = sources[i]
            if isinstance(source, Future):
                source = from_future(source)

            sad = SingleAssignmentDisposable()

            sad.disposable = source.subscribe(
                create_on_next(i),
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler,
            )

            subscriptions.append(sad)

        return CompositeDisposable(subscriptions)

    return Observable(subscribe=subscribe)


__all__ = ["combine_throttle_"]
