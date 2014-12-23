from rx import Observable, AnonymousObservable
from rx.internal.utils import adapt_call
from rx.internal import extensionmethod


@extensionmethod(Observable, alias="filter")
def where(self, predicate):
    """Filters the elements of an observable sequence based on a predicate
    by incorporating the element's index.

    1 - source.filter(lambda value: value < 10)
    2 - source.filter(lambda value, index: value < 10 or index < 10)

    Keyword arguments:
    predicate -- A function to test each source element for a conditio; the
        second parameter of the function represents the index of the source
        element.

    Returns an observable sequence that contains elements from the input
    sequence that satisfy the condition.
    """

    predicate = adapt_call(predicate)
    parent = self

    def subscribe(observer):
        count = [0]

        def on_next(value):
            should_run = False
            try:
                should_run = predicate(value, count[0])
            except Exception as ex:
                observer.on_error(ex)
                return
            else:
                count[0] += 1

            if should_run:
                observer.on_next(value)

        return parent.subscribe(on_next, observer.on_error, observer.on_completed)
    return AnonymousObservable(subscribe)
