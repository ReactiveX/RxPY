from rx.core import ObservableBase, AnonymousObservable
from rx.core.typing import Predicate, PredicateIndexed


# pylint: disable=W0622
def filter(source: ObservableBase,
           predicate: Predicate = None,
           predicate_indexed: PredicateIndexed = None):
    """Filters the elements of an observable sequence based on a predicate
    by incorporating the element's index.

    1 - source.filter(lambda value: value < 10)

    Keyword arguments:
    source -- Observable sequence to filter.
    predicate --  A function to test each source element for a
        condition.
    predicate_indexed -- A function to test each source element for a
        condition; the second parameter of the function represents the
        index of the source element.

    Returns an observable sequence that contains elements from the input
    sequence that satisfy the condition.
    """

    def subscribe(observer, scheduler=None):
        count = 0

        def send(value):
            nonlocal count

            try:
                should_run = predicate(value) if predicate else predicate_indexed(value, count)
            except Exception as ex:  # By design. pylint: disable=W0703
                observer.throw(ex)
                return
            else:
                count += 1

            if should_run:
                observer.send(value)

        return source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)


