import logging
from typing import Callable

from rx import empty
from rx.core import Observable, typing
from rx.internal.utils import add_ref
from rx.internal import noop
from rx.disposable import SingleAssignmentDisposable, SerialDisposable, CompositeDisposable, RefCountDisposable
from rx.subjects import Subject
from rx import operators as ops

log = logging.getLogger("Rx")


def _window(window_openings=None, window_closing_mapper=None) -> Callable[[Observable], Observable]:
    # Make it possible to call window with a single unnamed parameter
    if not isinstance(window_openings, typing.Observable) and callable(window_openings):
        window_closing_mapper = window_openings
        window_openings = None

    def window(source: Observable) -> Observable:
        """Projects each element of an observable sequence into zero or
        more windows.

        Args:
            source: Source observable to project into windows.

        Returns:
            An observable sequence of windows.
        """

        if window_openings and not window_closing_mapper:
            return observable_window_with_boundaries(source, window_openings)

        if not window_openings and window_closing_mapper:
            return observable_window_with_closing_mapper(source, window_closing_mapper)

        return observable_window_with_openings(source, window_openings, window_closing_mapper)
    return window


def observable_window_with_openings(self, window_openings, window_closing_mapper):

    def mapper(args):
        _, window = args
        return window

    return window_openings.pipe(
        ops.group_join(
            self,
            window_closing_mapper,
            lambda _: empty(),
            ),
        ops.map(mapper),
        )

def observable_window_with_boundaries(self, window_boundaries):
    source = self

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


def observable_window_with_closing_mapper(self, window_closing_mapper):
    source = self

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
