from typing import Any, List, Optional, Tuple, TypeVar
import threading

from reactivex import Observable, abc
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable

T = TypeVar("T")


def combine_latest_(*sources: Observable[T]) -> Observable[Tuple[T, ...]]:
    """
    Combine multiple observable sequences into one by emitting a tuple
    containing the latest values from each source whenever any source emits.

    The resulting observable emits only after all sources have emitted at
    least once, and then emits again whenever any individual source produces
    a new value. Completion occurs when all sources complete, or an error
    is propagated immediately if any source fails.

    Args:
        *sources: Variable number of observable sources to combine.

    Returns:
        Observable[Tuple[T, ...]]: An observable that emits tuples with the
        most recent values from all provided sources.

    Raises:
        ValueError: If no observable sources are provided.

    Examples:
        >>> obs = combine_latest_(obs1, obs2, obs3)
        >>> obs.subscribe(print)
    """
    if not sources:
        raise ValueError("At least one observable source must be provided.")

    parent = sources[0]
    lock = getattr(parent, "lock", threading.RLock())

    def subscribe(
        observer: abc.ObserverBase[Any],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> CompositeDisposable:
        n = len(sources)
        has_value: List[bool] = [False] * n
        is_done: List[bool] = [False] * n
        values: List[Optional[T]] = [None] * n
        has_value_all = False

        def _next(i: int) -> None:
            nonlocal has_value_all
            has_value[i] = True
            has_value_all = all(has_value)

            if has_value_all:
                observer.on_next(tuple(values))
            elif all(done for j, done in enumerate(is_done) if j != i):
                observer.on_completed()

        def _done(i: int) -> None:
            is_done[i] = True
            if all(is_done):
                observer.on_completed()

        subscriptions: List[SingleAssignmentDisposable] = [
            SingleAssignmentDisposable() for _ in range(n)
        ]

        for i, source in enumerate(sources):
            sad = subscriptions[i]

            def on_next(x: Any, index=i) -> None:
                with lock:
                    values[index] = x
                    _next(index)

            def on_completed(index=i) -> None:
                with lock:
                    _done(index)

            sad.disposable = source.subscribe(
                on_next,
                observer.on_error,
                on_completed,
                scheduler=scheduler,
            )

        return CompositeDisposable(subscriptions)

    return Observable(subscribe=subscribe)


__all__ = ["combine_latest_"]
