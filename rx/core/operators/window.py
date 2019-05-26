import logging
from typing import Callable, Any

from rx import empty
from rx.core import Observable
from rx.internal import noop
from rx.internal.utils import add_ref
from rx.disposable import SingleAssignmentDisposable, SerialDisposable, CompositeDisposable, RefCountDisposable
from rx.subjects import Subject
from rx import operators as ops

log = logging.getLogger("Rx")


def _window_with_openings(window_openings: Observable,
                          window_closing_mapper: Callable[[Any], Observable]
                          ) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """
    def window_with_openings(source: Observable) -> Observable:

        def mapper(args):
            _, window = args
            return window

        return window_openings.pipe(
            ops.group_join(
                source,
                window_closing_mapper,
                lambda _: empty(),
                ),
            ops.map(mapper),
            )
    return window_with_openings


def _window_with_boundaries(window_boundaries: Observable
                            ) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """
    def window_with_boundaries(source: Observable) -> Observable:

        def subscribe(observer, scheduler=None):
            window = [Subject()]
            d = CompositeDisposable()
            r = RefCountDisposable(d)

            observer.on_next(add_ref(window[0], r))

            def on_next_window(x):
                window[0].on_next(x)

            def on_error(err):
                window[0].on_error(err)
                observer.on_error(err)

            def on_completed():
                window[0].on_completed()
                observer.on_completed()

            d.add(source.subscribe_(on_next_window, on_error, on_completed, scheduler))

            def on_next_observer(w):
                window[0].on_completed()
                window[0] = Subject()
                observer.on_next(add_ref(window[0], r))

            d.add(window_boundaries.subscribe_(on_next_observer, on_error, on_completed, scheduler))
            return r
        return Observable(subscribe)
    return window_with_boundaries


def _window_with_closing_mapper(window_closing_mapper: Callable[[], Observable]
                                ) -> Observable:
    """Projects each element of an observable sequence into zero or
    more windows.

    Args:
        source: Source observable to project into windows.

    Returns:
        An observable sequence of windows.
    """
    def window_with_closing_mapper(source: Observable) -> Observable:

        def subscribe(observer, scheduler=None):
            m = SerialDisposable()
            d = CompositeDisposable(m)
            r = RefCountDisposable(d)
            window = [Subject()]

            observer.on_next(add_ref(window[0], r))

            def on_next(value):
                window[0].on_next(value)

            def on_error(error):
                window[0].on_error(error)
                observer.on_error(error)

            def on_completed():
                window[0].on_completed()
                observer.on_completed()

            d.add(source.subscribe_(on_next, on_error, on_completed, scheduler))

            def create_window_on_completed():
                try:
                    window_close = window_closing_mapper()
                except Exception as exception:
                    observer.on_error(exception)
                    return

                def on_completed():
                    window[0].on_completed()
                    window[0] = Subject()
                    observer.on_next(add_ref(window[0], r))
                    create_window_on_completed()

                m1 = SingleAssignmentDisposable()
                m.disposable = m1
                m1.disposable = window_close.pipe(ops.take(1)).subscribe_(noop, on_error, on_completed, scheduler)

            create_window_on_completed()
            return r
        return Observable(subscribe)
    return window_with_closing_mapper