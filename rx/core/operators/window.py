import logging
from typing import Callable, Any

from rx import empty
from rx.core import Observable
from rx.internal import noop
from rx.internal.utils import add_ref
from rx.disposable import SingleAssignmentDisposable, SerialDisposable, CompositeDisposable, RefCountDisposable
from rx.subject import Subject
from rx import operators as ops

log = logging.getLogger("Rx")


def _window_toggle(openings: Observable,
                   closing_mapper: Callable[[Any], Observable]
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


def _window(boundaries: Observable) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """
    def window(source: Observable) -> Observable:

        def subscribe(observer, scheduler=None):
            window_subject = Subject()
            d = CompositeDisposable()
            r = RefCountDisposable(d)

            observer.on_next(add_ref(window_subject, r))

            def on_next_window(x):
                window_subject.on_next(x)

            def on_error(err):
                window_subject.on_error(err)
                observer.on_error(err)

            def on_completed():
                window_subject.on_completed()
                observer.on_completed()

            d.add(source.subscribe_(on_next_window, on_error, on_completed, scheduler))

            def on_next_observer(w):
                nonlocal window_subject
                window_subject.on_completed()
                window_subject = Subject()
                observer.on_next(add_ref(window_subject, r))

            d.add(boundaries.subscribe_(on_next_observer, on_error, on_completed, scheduler))
            return r
        return Observable(subscribe)
    return window


def _window_when(closing_mapper: Callable[[], Observable]) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """
    def window_when(source: Observable) -> Observable:

        def subscribe(observer, scheduler=None):
            m = SerialDisposable()
            d = CompositeDisposable(m)
            r = RefCountDisposable(d)
            window = Subject()

            observer.on_next(add_ref(window, r))

            def on_next(value):
                window.on_next(value)

            def on_error(error):
                window.on_error(error)
                observer.on_error(error)

            def on_completed():
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
                m1.disposable = window_close.pipe(ops.take(1)).subscribe_(noop, on_error, on_completed, scheduler)

            create_window_on_completed()
            return r
        return Observable(subscribe)
    return window_when
