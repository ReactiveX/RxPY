import logging

from rx.core import AnonymousObservable, Observable, ObservableBase, typing
from rx.internal.utils import add_ref
from rx.internal import noop
from rx.disposables import SingleAssignmentDisposable, SerialDisposable, \
    CompositeDisposable, RefCountDisposable
from rx.subjects import Subject

log = logging.getLogger("Rx")


def window(self, window_openings=None, window_closing_mapper=None) -> ObservableBase:
    """Projects each element of an observable sequence into zero or more
    windows.

    Keyword arguments:
    window_openings -- Observable sequence whose elements denote the
        creation of windows.
    window_closing_mapper -- [Optional] A function invoked to define
        the closing of each produced window. It defines the boundaries
        of the produced windows (a window is started when the previous
        one is closed, resulting in non-overlapping windows).

    Returns an observable sequence of windows.
    """

    # Make it possible to call window with a single unnamed parameter
    if not isinstance(window_openings, typing.Observable) and callable(window_openings):
        window_closing_mapper = window_openings
        window_openings = None

    if window_openings and not window_closing_mapper:
        return observable_window_with_boundaries(self, window_openings)

    if not window_openings and window_closing_mapper:
        return observable_window_with_closing_mapper(self, window_closing_mapper)

    return observable_window_with_openings(self, window_openings, window_closing_mapper)

def observable_window_with_openings(self, window_openings, window_closing_mapper):
    return window_openings.group_join(self, window_closing_mapper, lambda _: Observable.empty(), lambda _, window: window)

def observable_window_with_boundaries(self, window_boundaries):
    source = self

    def subscribe(observer, scheduler=None):
        window = [Subject()]
        d = CompositeDisposable()
        r = RefCountDisposable(d)

        observer.send(add_ref(window[0], r))

        def send_window(x):
            window[0].send(x)

        def throw(err):
            window[0].throw(err)
            observer.throw(err)

        def close():
            window[0].close()
            observer.close()

        d.add(source.subscribe_callbacks(send_window, throw, close, scheduler))

        def send_observer(w):
            window[0].close()
            window[0] = Subject()
            observer.send(add_ref(window[0], r))

        d.add(window_boundaries.subscribe_callbacks(send_observer, throw, close, scheduler))
        return r
    return AnonymousObservable(subscribe)

def observable_window_with_closing_mapper(self, window_closing_mapper):
    source = self

    def subscribe(observer, scheduler=None):
        m = SerialDisposable()
        d = CompositeDisposable(m)
        r = RefCountDisposable(d)
        window = [Subject()]

        observer.send(add_ref(window[0], r))

        def send(value):
            window[0].send(value)

        def throw(error):
            window[0].throw(error)
            observer.throw(error)

        def close():
            window[0].close()
            observer.close()

        d.add(source.subscribe_callbacks(send, throw, close, scheduler))

        def create_window_close():
            try:
                window_close = window_closing_mapper()
            except Exception as exception:
                log.error("*** Exception: %s" % exception)
                observer.throw(exception)
                return

            def close():
                window[0].close()
                window[0] = Subject()
                observer.send(add_ref(window[0], r))
                create_window_close()

            m1 = SingleAssignmentDisposable()
            m.disposable = m1
            m1.disposable = window_close.take(1).subscribe_callbacks(noop, throw, close, scheduler)

        create_window_close()
        return r
    return AnonymousObservable(subscribe)
