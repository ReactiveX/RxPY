import logging
from typing import Any, Callable, Optional, Tuple, TypeVar

from reactivex import Observable, abc, empty
from reactivex import operators as ops
from reactivex.disposable import (
    CompositeDisposable,
    RefCountDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import add_ref, noop
from reactivex.subject import Subject

log = logging.getLogger("Rx")

_T = TypeVar("_T")


def window_toggle_(
    openings: Observable[Any], closing_mapper: Callable[[Any], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """

    def window_toggle(source: Observable[_T]) -> Observable[Observable[_T]]:
        def mapper(args: Tuple[Any, Observable[_T]]):
            _, window = args
            return window

        return openings.pipe(
            ops.group_join(
                source,
                closing_mapper,
                lambda _: empty(),
            ),
            ops.map(mapper),
        )

    return window_toggle


def window_(
    boundaries: Observable[Any],
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """

    def window(source: Observable[_T]) -> Observable[Observable[_T]]:
        def subscribe(
            observer: abc.ObserverBase[Observable[_T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            window_subject: Subject[_T] = Subject()
            d = CompositeDisposable()
            r = RefCountDisposable(d)

            observer.on_next(add_ref(window_subject, r))

            def on_next_window(x: _T) -> None:
                window_subject.on_next(x)

            def on_error(err: Exception) -> None:
                window_subject.on_error(err)
                observer.on_error(err)

            def on_completed() -> None:
                window_subject.on_completed()
                observer.on_completed()

            d.add(
                source.subscribe(
                    on_next_window, on_error, on_completed, scheduler=scheduler
                )
            )

            def on_next_observer(w: Observable[_T]):
                nonlocal window_subject
                window_subject.on_completed()
                window_subject = Subject()
                observer.on_next(add_ref(window_subject, r))

            d.add(
                boundaries.subscribe(
                    on_next_observer, on_error, on_completed, scheduler=scheduler
                )
            )
            return r

        return Observable(subscribe)

    return window


def window_when_(
    closing_mapper: Callable[[], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[Observable[_T]]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """

    def window_when(source: Observable[_T]) -> Observable[Observable[_T]]:
        def subscribe(
            observer: abc.ObserverBase[Observable[_T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            m = SerialDisposable()
            d = CompositeDisposable(m)
            r = RefCountDisposable(d)
            window: Subject[_T] = Subject()

            observer.on_next(add_ref(window, r))

            def on_next(value: _T) -> None:
                window.on_next(value)

            def on_error(error: Exception) -> None:
                window.on_error(error)
                observer.on_error(error)

            def on_completed() -> None:
                window.on_completed()
                observer.on_completed()

            d.add(
                source.subscribe(on_next, on_error, on_completed, scheduler=scheduler)
            )

            def create_window_on_completed():
                try:
                    window_close = closing_mapper()
                except Exception as exception:
                    observer.on_error(exception)
                    return

                def on_completed():
                    nonlocal window
                    window.on_completed()
                    window = Subject()
                    observer.on_next(add_ref(window, r))
                    create_window_on_completed()

                m1 = SingleAssignmentDisposable()
                m.disposable = m1
                m1.disposable = window_close.pipe(ops.take(1)).subscribe(
                    noop, on_error, on_completed, scheduler=scheduler
                )

            create_window_on_completed()
            return r

        return Observable(subscribe)

    return window_when


__all__ = ["window_", "window_when_", "window_toggle_"]
