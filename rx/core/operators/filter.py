from typing import Callable

from rx.core import AnonymousObservable, Observable
from rx.core.typing import Predicate, PredicateIndexed, Scheduler, Observer, Disposable


# pylint: disable=W0622
def filter(predicate: Predicate) -> Callable[[Observable], Observable]:
    """Filters the elements of an observable sequence based on a
    predicate by incorporating the element's index.

    Example:
        >>> filter(lambda value: value < 10)(source)

    Args:
        predicate --  A function to test each source element for a
            condition.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence that contains elements from the input
        sequence that satisfy the condition.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(observer: Observer, scheduler: Scheduler) -> Disposable:
            def on_next(value):
                try:
                    should_run = predicate(value)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return

                if should_run:
                    observer.on_next(value)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial


def filteri(predicate_indexed: PredicateIndexed = None) -> Callable[[Observable], Observable]:
    """Filters the elements of an observable sequence based on a
    predicate by incorporating the element's index.

    Example:
        >>> filter(lambda value, index: (value + index) < 10)(source)

    Args:
        predicate -- A function to test each source element for a
            condition; the second parameter of the function represents the
            index of the source element.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence that contains elements from the input
        sequence that satisfy the condition.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(observer: Observer, scheduler: Scheduler):
            count = 0

            def on_next(value):
                nonlocal count
                try:
                    should_run = predicate_indexed(value, count)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return
                else:
                    count += 1

                if should_run:
                    observer.on_next(value)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial
