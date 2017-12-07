from rx import Observable, AnonymousObservable
from rx.internal import extensionmethod

def _to_set(source, set_type):
    def subscribe(observer, scheduler=None):
        s = set_type()

        def close():
            observer.send(s)
            observer.close()

        return source.subscribe_callbacks(s.add, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)


@extensionmethod(Observable)
def to_set(self):
    """Converts the observable sequence to a set.

    Returns {Observable} An observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    return _to_set(self, set)
