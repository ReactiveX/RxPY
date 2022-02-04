import logging
from typing import Any, Callable, Optional, TypeVar

from rx import empty
from rx import operators as ops
from rx.core import Observable, abc
from rx.disposable import (
    CompositeDisposable,
    RefCountDisposable,
    SerialDisposable,
    SingleAssignmentDisposable,
)
from rx.internal import noop
from rx.internal.utils import add_ref
from rx.subject import Subject

log = logging.getLogger("Rx")

_T = TypeVar("_T")


def _window_toggle(
    openings: Observable, closing_mapper: Callable[[Any], Observable]
) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """

    def window_toggle(source: Observable) -> Observable:
        def mapper(args):
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


def _window(
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

            d.add(source.subscribe_(on_next_window, on_error, on_completed, scheduler))

            def on_next_observer(w: Observable[_T]):
                nonlocal window_subject
                window_subject.on_completed()
                window_subject = Subject()
                observer.on_next(add_ref(window_subject, r))

            d.add(
                boundaries.subscribe_(
                    on_next_observer, on_error, on_completed, scheduler
                )
            )
            return r

        return Observable(subscribe)

    return window


def _window_when(
    closing_mapper: Callable[[], Observable[_T]]
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

            d.add(source.subscribe_(on_next, on_error, on_completed, scheduler))

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
                m1.disposable = window_close.pipe(ops.take(1)).subscribe_(
                    noop, on_error, on_completed, scheduler
                )

            create_window_on_completed()
            return r

        return Observable(subscribe)

    return window_when
