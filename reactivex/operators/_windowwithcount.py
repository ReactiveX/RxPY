import logging
from typing import TypeVar

from reactivex import Observable, abc
from reactivex.disposable import RefCountDisposable, SingleAssignmentDisposable
from reactivex.internal import ArgumentOutOfRangeException, add_ref, curry_flip
from reactivex.subject import Subject

log = logging.getLogger("Rx")

_T = TypeVar("_T")


@curry_flip
def window_with_count_(
    source: Observable[_T],
    count: int,
    skip: int | None = None,
) -> Observable[Observable[_T]]:
    """Projects each element of an observable sequence into zero or more
    windows which are produced based on element count information.

    Examples:
        >>> source.pipe(window_with_count(10))
        >>> source.pipe(window_with_count(10, 1))
        >>> window_with_count(10)(source)

    Args:
        source: Source observable to window.
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

    def subscribe(
        observer: abc.ObserverBase[Observable[_T]],
        scheduler: abc.SchedulerBase | None = None,
    ):
        m = SingleAssignmentDisposable()
        refCountDisposable = RefCountDisposable(m)
        n = [0]
        q: list[Subject[_T]] = []

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


__all__ = ["window_with_count_"]
