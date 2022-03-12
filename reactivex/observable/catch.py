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


def catch_with_iterable_(sources: Iterable[Observable[_T]]) -> Observable[_T]:

    """Continues an observable sequence that is terminated by an
    exception with the next observable sequence.

    Examples:
        >>> res = catch([xs, ys, zs])
        >>> res = reactivex.catch(src for src in [xs, ys, zs])

    Args:
        sources: an Iterable of observables. Thus a generator is accepted.

    Returns:
        An observable sequence containing elements from consecutive
        source sequences until a source sequence terminates
        successfully.
    """

    sources_ = iter(sources)

    def subscribe(
        observer: abc.ObserverBase[_T], scheduler_: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler_ or CurrentThreadScheduler.singleton()

        subscription = SerialDisposable()
        cancelable = SerialDisposable()
        last_exception = None
        is_disposed = False

        def action(scheduler: abc.SchedulerBase, state: Any = None) -> None:
            def on_error(exn: Exception) -> None:
                nonlocal last_exception
                last_exception = exn
                cancelable.disposable = _scheduler.schedule(action)

            if is_disposed:
                return

            try:
                current = next(sources_)
            except StopIteration:
                if last_exception:
                    observer.on_error(last_exception)
                else:
                    observer.on_completed()
            except Exception as ex:  # pylint: disable=broad-except
                observer.on_error(ex)
            else:
                d = SingleAssignmentDisposable()
                subscription.disposable = d
                d.disposable = current.subscribe(
                    observer.on_next,
                    on_error,
                    observer.on_completed,
                    scheduler=scheduler_,
                )

        cancelable.disposable = _scheduler.schedule(action)

        def dispose() -> None:
            nonlocal is_disposed
            is_disposed = True

        return CompositeDisposable(subscription, cancelable, Disposable(dispose))

    return Observable(subscribe)


__all__ = ["catch_with_iterable_"]
