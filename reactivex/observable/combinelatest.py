from threading import RLock
from typing import Any

from reactivex import Observable, abc
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable


def combine_latest_(*sources: Observable[Any]) -> Observable[tuple[Any, ...]]:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever any of the
    observable sequences produces an element.

    The result emits only once every source has produced at least one
    element, and then again whenever any source produces a new element.

    Examples:
        >>> obs = combine_latest(obs1, obs2, obs3)

    Args:
        sources: Observable sources to combine.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources into a tuple.

    Raises:
        ValueError: If no observable sources are given.
    """

    if not sources:
        raise ValueError("combine_latest() requires at least one source.")

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: abc.SchedulerBase | None = None
    ) -> CompositeDisposable:
        n = len(sources)
        lock = RLock()
        has_value = [False] * n
        has_value_all = False
        is_done = [False] * n
        values: list[Any] = [None] * n

        def _next(i: int) -> None:
            nonlocal has_value_all

            has_value[i] = True
            has_value_all = has_value_all or all(has_value)

            if has_value_all:
                observer.on_next(tuple(values))
            elif all(done for j, done in enumerate(is_done) if j != i):
                observer.on_completed()

        def done(i: int) -> None:
            is_done[i] = True
            if all(is_done):
                observer.on_completed()

        subscriptions = [SingleAssignmentDisposable() for _ in range(n)]

        def func(i: int) -> None:
            def on_next(x: Any) -> None:
                with lock:
                    values[i] = x
                    _next(i)

            def on_completed() -> None:
                with lock:
                    done(i)

            subscriptions[i].disposable = sources[i].subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )

        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)

    return Observable(subscribe)


__all__ = ["combine_latest_"]
