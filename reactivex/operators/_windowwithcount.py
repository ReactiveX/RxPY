import logging
from typing import Callable, List, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.disposable import RefCountDisposable, SingleAssignmentDisposable
from reactivex.internal import ArgumentOutOfRangeException, add_ref
from reactivex.subject import Subject

log = logging.getLogger("Rx")

_T = TypeVar("_T")


def window_with_count_(
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

    skip_ = skip if skip is not None else count

    if skip_ <= 0:
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
                if c >= 0 and c % skip_ == 0:
                    s = q.pop(0)
                    s.on_completed()

                n[0] += 1
                if (n[0] % skip_) == 0:
                    create_window()

            def on_error(exception: Exception) -> None:
                while q:
                    q.pop(0).on_error(exception)
                observer.on_error(exception)

            def on_completed() -> None:
                while q:
                    q.pop(0).on_completed()
                observer.on_completed()

            m.disposable = source.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler
            )
            return refCountDisposable

        return Observable(subscribe)

    return window_with_count


__all__ = ["window_with_count_"]
