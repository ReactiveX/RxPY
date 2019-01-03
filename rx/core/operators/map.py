from typing import Callable, Any
from rx.core import AnonymousObservable, Observable
from rx.core.typing import Mapper, MapperIndexed, Observer, Disposable, Scheduler


# By design. pylint: disable=W0622
def map(mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """Project each element of an observable sequence into a new form
    by incorporating the element's index.

    Example:
        >>> map(lambda value: value * 10)

    Args:
        mapper: A transform function to apply to each source element; the
            second parameter of the function represents the index of the
            source element

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence whose elements are the result of invoking
        the transform function on each element of the source.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(obv: Observer, scheduler: Scheduler) -> Disposable:
            def on_next(value: Any) -> None:
                try:
                    result = mapper(value)
                except Exception as err:  # pylint: disable=broad-except
                    obv.on_error(err)
                else:
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
        mapper_indexed: A transform function to apply to each source
            element; the second parameter of the function represents the
            index of the source element.

    Returns:
        A operator function that takes an observable source and returns
        an observable sequence whose elements are the result of invoking
        the transform function on each element of the source.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(obv: Observer, scheduler: Scheduler) -> Disposable:
            count = 0

            def on_next(value: Any) -> None:
                nonlocal count

                try:
                    result = mapper_indexed(value, count)
                except Exception as err:  # pylint: disable=broad-except
                    obv.on_error(err)
                else:
                    count += 1
                    obv.on_next(result)

            return source.subscribe_(on_next, obv.on_error, obv.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial
