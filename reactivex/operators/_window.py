import logging
from collections.abc import Callable
from typing import Any, TypeVar

from reactivex import Observable, abc, empty
from reactivex import operators as ops
from reactivex.disposable import (
    CompositeDisposable,
    RefCountDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from reactivex.internal import add_ref, curry_flip, noop
from reactivex.subject import Subject

log = logging.getLogger("Rx")

_T = TypeVar("_T")


@curry_flip
def window_toggle_(
    source: Observable[_T],
    openings: Observable[Any],
    closing_mapper: Callable[[Any], Observable[Any]],
) -> Observable[Observable[_T]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.
        openings: Observable that triggers window opening.
        closing_mapper: Function to create closing observable.

    Returns:
        An observable sequence of windows.
    """

    def mapper(args: tuple[Any, Observable[_T]]):
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


@curry_flip
def window_(
    source: Observable[_T],
    boundaries: Observable[Any],
) -> Observable[Observable[_T]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.
        boundaries: Observable that triggers window boundaries.

    Returns:
        An observable sequence of windows.
    """

    def subscribe(
        observer: abc.ObserverBase[Observable[_T]],
        scheduler: abc.SchedulerBase | None = None,
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


@curry_flip
def window_when_(
    source: Observable[_T],
    closing_mapper: Callable[[], Observable[Any]],
) -> Observable[Observable[_T]]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.
        closing_mapper: Function that returns an observable signaling window close.

    Returns:
        An observable sequence of windows.
    """

    def subscribe(
        observer: abc.ObserverBase[Observable[_T]],
        scheduler: abc.SchedulerBase | None = None,
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

        d.add(source.subscribe(on_next, on_error, on_completed, scheduler=scheduler))

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


__all__ = ["window_", "window_when_", "window_toggle_"]
