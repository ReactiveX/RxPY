from typing import Callable
from rx.core import ObservableBase, AnonymousObservable


def some(predicate=None) -> Callable[[ObservableBase], ObservableBase]:
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

    def partial(source: ObservableBase) -> ObservableBase:
        def subscribe(observer, scheduler=None):
            def on_next(_):
                observer.on_next(True)
                observer.on_completed()

            def on_error():
                observer.on_next(False)
                observer.on_completed()
            return source.subscribe_(on_next, observer.on_error, on_error, scheduler)

        return source.filter(predicate).some() if predicate else AnonymousObservable(subscribe)
    return partial
