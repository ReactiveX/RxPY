from typing import Callable
from rx.core import AnonymousObservable, Observable
from rx.core.typing import Mapper, MapperIndexed, Observer, Disposable, Scheduler


# By design. pylint: disable=W0622
def map(mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    Example:
        >>> map(lambda value: value * 10)(source)

    Keyword arguments:
    mapper -- A transform function to apply to each source element; the
        second parameter of the function represents the index of the
        source element

    Returns:
        A function that takes an observable source and returns an
        observable sequence whose elements are the result of invoking
        the transform function on each element of the source.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(obv: Observer, scheduler: Scheduler) -> Disposable:
            print("map subscribe")

            def on_next(value):
                try:
                    result = mapper(value)
                except Exception as err:  # By design. pylint: disable=W0703
                    obv.on_error(err)
                else:
                    print("Map.on_next(%s)" % result)

                    obv.on_next(result)

            return source.subscribe_(on_next, obv.on_error, obv.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial


def mapi(mapper_indexed: MapperIndexed = None) -> Callable[[Observable], Observable]:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    Example:
        >>> ret = map(lambda value, index: value * value + index)(source)

    Args:
        mapper -- A transform function to apply to each source
            element; the second parameter of the function represents the
            index of the source element.

    Return:
        A function that takes an observable source and returns an
        observable sequence whose elements are the result of invoking
        the transform function on each element of the source.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(obv: Observer, scheduler: Scheduler) -> Disposable:
            count = 0

            def on_next(value):
                nonlocal count

                try:
                    result = mapper_indexed(value, count)
                except Exception as err:  # By design. pylint: disable=W0703
                    obv.on_error(err)
                else:
                    count += 1
                    obv.on_next(result)

            return source.subscribe_(on_next, obv.on_error, obv.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial
