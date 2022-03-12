from typing import Any, List, Optional, Tuple

from reactivex import Observable, abc
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable


def combine_latest_(*sources: Observable[Any]) -> Observable[Tuple[Any, ...]]:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever any of the
    observable sequences produces an element.

    Examples:
        >>> obs = combine_latest(obs1, obs2, obs3)

    Returns:
        An observable sequence containing the result of combining
        elements of the sources into a tuple.
    """

    parent = sources[0]

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> CompositeDisposable:

        n = len(sources)
        has_value = [False] * n
        has_value_all = [False]
        is_done = [False] * n
        values = [None] * n

        def _next(i: Any) -> None:
            has_value[i] = True

            if has_value_all[0] or all(has_value):
                res = tuple(values)
                observer.on_next(res)

            elif all([x for j, x in enumerate(is_done) if j != i]):
                observer.on_completed()

            has_value_all[0] = all(has_value)

        def done(i: Any) -> None:
            is_done[i] = True
            if all(is_done):
                observer.on_completed()

        subscriptions: List[Optional[SingleAssignmentDisposable]] = [None] * n

        def func(i: int) -> None:
            subscriptions[i] = SingleAssignmentDisposable()

            def on_next(x: Any) -> None:
                with parent.lock:
                    values[i] = x
                    _next(i)

            def on_completed() -> None:
                with parent.lock:
                    done(i)

            subscription = subscriptions[i]
            assert subscription
            subscription.disposable = sources[i].subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )

        for idx in range(n):
            func(idx)
        return CompositeDisposable(subscriptions)

    return Observable(subscribe)


__all__ = ["combine_latest_"]
