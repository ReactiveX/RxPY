from rx.core import ObservableBase, AnonymousObservable


def some(source, predicate=None) -> ObservableBase:
    """Determines whether some element of an observable sequence satisfies a
    condition if present, else if some items are in the sequence.

    Example:
    result = source.some()
    result = source.some(lambda x: x > 3)

    Keyword arguments:
    predicate -- A function to test each element for a condition.

    Returns an observable sequence containing a single element
    determining whether some elements in the source sequence pass the test
    in the specified predicate if given, else if some items are in the
    sequence.
    """

    def subscribe(observer, scheduler=None):
        def send(_):
            observer.send(True)
            observer.close()
        def throw():
            observer.send(False)
            observer.close()
        return source.subscribe_(send, observer.throw, throw, scheduler)

    return source.filter(predicate).some() if predicate else AnonymousObservable(subscribe)
