from typing import Callable
from rx.core import AnonymousObservable, Observable
from rx.core.typing import Predicate


def find_value(source: Observable, predicate: Predicate, yield_index):
    def subscribe(observer, scheduler=None):
        i = [0]

        def on_next(x):
            should_run = False
            try:
                should_run = predicate(x, i, source)
            except Exception as ex:
                observer.on_error(ex)
                return

            if should_run:
                observer.on_next(i[0] if yield_index else x)
                observer.on_completed()
            else:
                i[0] += 1

        def on_completed():
            observer.on_next(-1 if yield_index else None)
            observer.on_completed()

        return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
    return AnonymousObservable(subscribe)


def find(predicate: Predicate) -> Callable[[Observable], Observable]:
    """Searches for an element that matches the conditions defined by
    the specified predicate, and returns the first occurrence within the
    entire Observable sequence.

    Keyword arguments:
        predicate -- The predicate that defines the conditions of the
            element to search for.

    Returns:
        A function that takes an observable source and returns an
        observable sequence with the first element that matches the
        conditions defined by the specified predicate, if found
        otherwise, None.
    """

    def partial(source: Observable) -> Observable:
        return find_value(source, predicate, False)
    return partial
