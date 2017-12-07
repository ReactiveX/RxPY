import logging

from rx import AnonymousObservable, Observable
from rx.internal.utils import add_ref
from rx.disposables import SingleAssignmentDisposable, RefCountDisposable
from rx.internal.exceptions import ArgumentOutOfRangeException
from rx.subjects import Subject
from rx.internal import extensionmethod

log = logging.getLogger("Rx")


@extensionmethod(Observable)
def window_with_count(self, count, skip=None):
    """Projects each element of an observable sequence into zero or more
    windows which are produced based on element count information.

    1 - xs.window_with_count(10)
    2 - xs.window_with_count(10, 1)

    count -- Length of each window.
    skip -- [Optional] Number of elements to skip between creation of
        consecutive windows. If not specified, defaults to the count.

    Returns an observable sequence of windows.
    """

    source = self
    if count <= 0:
        raise ArgumentOutOfRangeException()

    if skip is None:
        skip = count

    if skip <= 0:
        raise ArgumentOutOfRangeException()

    def subscribe(observer):
        m = SingleAssignmentDisposable()
        refCountDisposable = RefCountDisposable(m)
        n = [0]
        q = []

        def create_window():
            s = Subject()
            q.append(s)
            observer.send(add_ref(s, refCountDisposable))

        create_window()

        def send(x):
            for item in q:
                item.send(x)

            c = n[0] - count + 1
            if c >= 0 and c % skip == 0:
                s = q.pop(0);
                s.close()

            n[0] += 1
            if (n[0] % skip) == 0:
                create_window()

        def throw(exception):
            while len(q):
                q.pop(0).throw(exception)
            observer.throw(exception)

        def close():
            while len(q):
                q.pop(0).close()
            observer.close()

        m.disposable = source.subscribe_callbacks(send, throw, close)
        return refCountDisposable
    return AnonymousObservable(subscribe)

