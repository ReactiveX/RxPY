from typing import Callable
from rx.core import ObservableBase as Observable


def buffer(buffer_openings=None, buffer_closing_mapper=None) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or more
    buffers.

    Args:
        buffer_openings -- Observable sequence whose elements denote the
            creation of windows.
        buffer_closing_mapper -- [optional] A function invoked to define
            the closing of each produced window. If a closing mapper
            function is specified for the first parameter, this parameter is
            ignored.

    Returns:
        A function that takes an observable source and retuerns an
        observable sequence of windows.
    """

    def partial(source: Observable) -> Observable:
        return source.window(buffer_openings, buffer_closing_mapper).flat_map(lambda item: item.to_iterable().map(list))
    return partial


def buffer_with_count(count: int, skip: int = None) -> Callable[[Observable], Observable]:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on element count information.

    Examples:
        >>> res = buffer_with_count(10)(xs)
        >>> res = buffer_with_count(10, 1)(xs)

    Keyword parameters:
    count -- Length of each buffer.
    skip -- [Optional] Number of elements to skip between
        creation of consecutive buffers. If not provided, defaults to
        the count.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of buffers.
    """

    def partial(source: Observable) -> Observable:
        nonlocal skip

        if skip is None:
            skip = count

        def mapper(value):
            return value.to_iterable().map(list)

        def predicate(value):
            return len(value) > 0

        return source.window_with_count(count, skip).flat_map(mapper).filter(predicate)
    return partial
