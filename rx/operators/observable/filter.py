from typing import Any

from rx.core import AnonymousObservable, ObservableBase
from rx.core.typing import Predicate, PredicateIndexed, Scheduler, Observable, Observer, Disposable


# pylint: disable=W0622
def filter(predicate: Predicate = None, predicate_indexed: PredicateIndexed = None):
    """Filters the elements of an observable sequence based on a predicate
    by incorporating the element's index.

    1 - source.filter(lambda value: value < 10)

    Keyword arguments:
    source -- Observable sequence to filter.
    predicate --  A function to test each source element for a
        condition.

    Returns an observable sequence that contains elements from the input
    sequence that satisfy the condition.
    """

    def partial(source: ObservableBase):
        def subscribe(observer, scheduler: Scheduler) -> Disposable:
            def on_next(value):
                try:
                    should_run = predicate(value)
                except Exception as ex:  # By design. pylint: disable=W0703
                    observer.on_error(ex)
                    return

                if should_run:
                    observer.on_next(value)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial


def filteri(predicate: PredicateIndexed = None):
    """Filters the elements of an observable sequence based on a predicate
    by incorporating the element's index.

    1 - source.filter(lambda value, index: (value + index) < 10)

    Keyword arguments:
    source -- Observable sequence to filter.
    predicate -- A function to test each source element for a
        condition; the second parameter of the function represents the
        index of the source element.

    Returns an observable sequence that contains elements from the input
    sequence that satisfy the condition.
    """

    def partial(source: ObservableBase):
        def subscribe(observer, scheduler: Scheduler):
            count = 0

            def on_next(value):
                nonlocal count
                try:
                    should_run = predicate(value, count)
                except Exception as ex:  # By design. pylint: disable=W0703
                    observer.on_error(ex)
                    return
                else:
                    count += 1

                if should_run:
                    observer.on_next(value)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial
