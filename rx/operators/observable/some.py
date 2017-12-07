from rx.core import Observable, AnonymousObservable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def some(self, predicate=None):
    """Determines whether some element of an observable sequence satisfies a
    condition if present, else if some items are in the sequence.

    Example:
    result = source.some()
    result = source.some(lambda x: x > 3)

    Keyword arguments:
    predicate -- A function to test each element for a condition.

    Returns {Observable} an observable sequence containing a single element
    determining whether some elements in the source sequence pass the test
    in the specified predicate if given, else if some items are in the
    sequence.
    """

    source = self
    def subscribe(observer):
        def send(_):
            observer.send(True)
            observer.close()
        def throw():
            observer.send(False)
            observer.close()
        return source.subscribe_callbacks(send, observer.throw, throw)

    return source.filter(predicate).some() if predicate else AnonymousObservable(subscribe)
