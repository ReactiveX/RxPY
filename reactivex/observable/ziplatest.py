from collections.abc import Callable
from threading import RLock
from typing import Any

from reactivex import Observable, abc, from_future
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable
from reactivex.internal import is_future


def zip_latest_(*sources: Observable[Any]) -> Observable[tuple[Any, ...]]:
    """Pair the latest pending value from every source in each round.

    A faster source replaces its pending value instead of building a queue.
    A completed source may contribute its final pending value to one last tuple.
    """
    if not sources:
        raise ValueError("zip_latest() requires at least one source.")

    def subscribe(
        observer: abc.ObserverBase[tuple[Any, ...]],
        scheduler: abc.SchedulerBase | None = None,
    ) -> CompositeDisposable:
        lock = RLock()
        values: list[Any] = [None] * len(sources)
        completed = [False] * len(sources)
        pending = 0
        full_mask = (1 << len(sources)) - 1
        stopped = False
        subscriptions = [SingleAssignmentDisposable() for _ in sources]
        group = CompositeDisposable(subscriptions)

        def complete() -> None:
            nonlocal stopped
            stopped = True
            group.dispose()
            observer.on_completed()

        def on_error(error: Exception) -> None:
            nonlocal stopped
            with lock:
                if stopped:
                    return
                stopped = True
                group.dispose()
                observer.on_error(error)

        def create_on_next(index: int) -> Callable[[Any], None]:
            def on_next(value: Any) -> None:
                nonlocal pending
                with lock:
                    if stopped:
                        return
                    values[index] = value
                    pending |= 1 << index
                    if pending == full_mask:
                        pending = 0
                        observer.on_next(tuple(values))
                        if not stopped and any(completed):
                            complete()

            return on_next

        def create_on_completed(index: int) -> Callable[[], None]:
            def on_completed() -> None:
                with lock:
                    if stopped:
                        return
                    completed[index] = True
                    if not pending & (1 << index):
                        complete()

            return on_completed

        for index, source in enumerate(sources):
            if stopped:
                break
            if is_future(source):
                source = from_future(source)
            subscriptions[index].disposable = source.subscribe(
                create_on_next(index),
                on_error,
                create_on_completed(index),
                scheduler=scheduler,
            )

        return group

    return Observable(subscribe)


__all__ = ["zip_latest_"]
