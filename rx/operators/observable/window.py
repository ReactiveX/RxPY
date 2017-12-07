import logging

from rx import AnonymousObservable, Observable
from rx.internal.utils import add_ref
from rx.internal import noop
from rx.disposables import SingleAssignmentDisposable, SerialDisposable, \
    CompositeDisposable, RefCountDisposable
from rx.subjects import Subject
from rx.internal import extensionmethod

log = logging.getLogger("Rx")


@extensionmethod(Observable)
def window(self, window_openings=None, window_closing_selector=None):
    """Projects each element of an observable sequence into zero or more
    windows.

    Keyword arguments:
    :param Observable window_openings: Observable sequence whose elements
        denote the creation of windows.
    :param types.FunctionType window_closing_selector: [Optional] A function
        invoked to define the closing of each produced window. It defines the
        boundaries of the produced windows (a window is started when the
        previous one is closed, resulting in non-overlapping windows).

    :returns: An observable sequence of windows.
    :rtype: Observable[Observable]
    """

    # Make it possible to call window with a single unnamed parameter
    if not isinstance(window_openings, Observable) and callable(window_openings):
        window_closing_selector = window_openings
        window_openings = None

    if window_openings and not window_closing_selector:
        return observable_window_with_boundaries(self, window_openings)

    if not window_openings and window_closing_selector:
        return observable_window_with_closing_selector(self, window_closing_selector)

    return observable_window_with_openings(self, window_openings, window_closing_selector)

def observable_window_with_openings(self, window_openings, window_closing_selector):
    return window_openings.group_join(self, window_closing_selector, lambda _: Observable.empty(), lambda _, window: window)

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

def observable_window_with_closing_selector(self, window_closing_selector):
    source = self

    def subscribe(observer, scheduler=None):
        m = SerialDisposable()
        d = CompositeDisposable(m)
        r = RefCountDisposable(d)
        window = [Subject()]

        observer.send(add_ref(window[0], r))

        def send(x):
            window[0].send(x)

        def throw(ex):
            window[0].throw(ex)
            observer.throw(ex)

        def close():
            window[0].close()
            observer.close()

        d.add(source.subscribe_callbacks(send, throw, close, scheduler))

        def create_window_close():
            try:
                window_close = window_closing_selector()
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
