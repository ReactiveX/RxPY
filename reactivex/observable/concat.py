from typing import Any, Iterable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.disposable import (
    CompositeDisposable,
    Disposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.scheduler import CurrentThreadScheduler

_T = TypeVar("_T")


def concat_with_iterable_(sources: Iterable[Observable[_T]]) -> Observable[_T]:
    def subscribe(
        observer: abc.ObserverBase[_T], scheduler_: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler_ or CurrentThreadScheduler.singleton()

        sources_ = iter(sources)

        subscription = SerialDisposable()
        cancelable = SerialDisposable()
        is_disposed = False

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            nonlocal is_disposed
            if is_disposed:
                return

            def on_completed() -> None:
                cancelable.disposable = _scheduler.schedule(action)

            try:
                current = next(sources_)
            except StopIteration:
                observer.on_completed()
            except Exception as ex:  # pylint: disable=broad-except
                observer.on_error(ex)
            else:
                d = SingleAssignmentDisposable()
                subscription.disposable = d
                d.disposable = current.subscribe(
                    observer.on_next,
                    observer.on_error,
                    on_completed,
                    scheduler=scheduler_,
                )

        cancelable.disposable = _scheduler.schedule(action)

        def dispose() -> None:
            nonlocal is_disposed
            is_disposed = True

        return CompositeDisposable(subscription, cancelable, Disposable(dispose))

    return Observable(subscribe)


__all__ = ["concat_with_iterable_"]
