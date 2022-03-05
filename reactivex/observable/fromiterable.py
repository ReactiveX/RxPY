from typing import Any, Iterable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.disposable import CompositeDisposable, Disposable
from reactivex.scheduler import CurrentThreadScheduler

_T = TypeVar("_T")


def from_iterable_(
    iterable: Iterable[_T], scheduler: Optional[abc.SchedulerBase] = None
) -> Observable[_T]:
    """Converts an iterable to an observable sequence.

    Example:
        >>> from_iterable([1,2,3])

    Args:
        iterable: A Python iterable
        scheduler: An optional scheduler to schedule the values on.

    Returns:
        The observable sequence whose elements are pulled from the
        given iterable sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T], scheduler_: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or CurrentThreadScheduler.singleton()
        iterator = iter(iterable)
        disposed = False

        def action(_: abc.SchedulerBase, __: Any = None) -> None:
            nonlocal disposed

            try:
                while not disposed:
                    value = next(iterator)
                    observer.on_next(value)
            except StopIteration:
                observer.on_completed()
            except Exception as error:  # pylint: disable=broad-except
                observer.on_error(error)

        def dispose() -> None:
            nonlocal disposed
            disposed = True

        disp = Disposable(dispose)
        return CompositeDisposable(_scheduler.schedule(action), disp)

    return Observable(subscribe)


__all__ = ["from_iterable_"]
