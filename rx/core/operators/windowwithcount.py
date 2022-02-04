import logging
from typing import Callable, List, Optional, TypeVar

from rx.core import Observable, abc
from rx.disposable import RefCountDisposable, SingleAssignmentDisposable
from rx.internal.exceptions import ArgumentOutOfRangeException
from rx.internal.utils import add_ref
from rx.subject import Subject

log = logging.getLogger("Rx")

_T = TypeVar("_T")


def _window_with_count(
    count: int, skip: Optional[int] = None
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    """Projects each element of an observable sequence into zero or more
    windows which are produced based on element count information.

    Examples:
        >>> window_with_count(10)
        >>> window_with_count(10, 1)

    Args:
        count: Length of each window.
        skip: [Optional] Number of elements to skip between creation of
            consecutive windows. If not specified, defaults to the
            count.

    Returns:
        An observable sequence of windows.
    """

    if count <= 0:
        raise ArgumentOutOfRangeException()

    if skip is None:
        skip = count

    if skip <= 0:
        raise ArgumentOutOfRangeException()

    def window_with_count(source: Observable[_T]) -> Observable[Observable[_T]]:
        def subscribe(
            observer: abc.ObserverBase[Observable[_T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            m = SingleAssignmentDisposable()
            refCountDisposable = RefCountDisposable(m)
            n = [0]
            q: List[Subject[_T]] = []

            def create_window():
                s: Subject[_T] = Subject()
                q.append(s)
                observer.on_next(add_ref(s, refCountDisposable))

            create_window()

            def on_next(x: _T) -> None:
                for item in q:
                    item.on_next(x)

                c = n[0] - count + 1
                if c >= 0 and c % skip == 0:
                    s = q.pop(0)
                    s.on_completed()

                n[0] += 1
                if (n[0] % skip) == 0:
                    create_window()

            def on_error(exception: Exception) -> None:
                while q:
                    q.pop(0).on_error(exception)
                observer.on_error(exception)

            def on_completed() -> None:
                while q:
                    q.pop(0).on_completed()
                observer.on_completed()

            m.disposable = source.subscribe_(on_next, on_error, on_completed, scheduler)
            return refCountDisposable

        return Observable(subscribe)

    return window_with_count


__all__ = ["_window_with_count"]
