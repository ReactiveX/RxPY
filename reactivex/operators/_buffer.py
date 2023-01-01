from typing import Any, Callable, List, Optional, TypeVar

from reactivex import Observable, compose
from reactivex import operators as ops
from reactivex.curry import curry_flip

_T = TypeVar("_T")


def buffer_(
    boundaries: Observable[Any],
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    return compose(
        ops.window(boundaries),
        ops.flat_map(ops.to_list()),
    )


def buffer_when_(
    closing_mapper: Callable[[], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    return compose(
        ops.window_when(closing_mapper),
        ops.flat_map(ops.to_list()),
    )


def buffer_toggle_(
    openings: Observable[Any], closing_mapper: Callable[[Any], Observable[Any]]
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    return compose(
        ops.window_toggle(openings, closing_mapper),
        ops.flat_map(ops.to_list()),
    )


@curry_flip(1)
def buffer_with_count_(
    source: Observable[_T], count: int, skip: Optional[int] = None
) -> Observable[List[_T]]:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on element count information.

    Examples:
        >>> res = buffer_with_count(10)(xs)
        >>> res = buffer_with_count(10, 1)(xs)

    Args:
        count: Length of each buffer.
        skip: [Optional] Number of elements to skip between
            creation of consecutive buffers. If not provided, defaults to
            the count.

    Returns:
        A function that takes an observable source and returns an
        observable sequence of buffers.
    """

    if skip is None:
        skip = count

    def mapper(value: Observable[_T]) -> Observable[List[_T]]:
        return value.pipe(
            ops.to_list(),
        )

    def predicate(value: List[_T]) -> bool:
        return len(value) > 0

    return source.pipe(
        ops.window_with_count(count, skip),
        ops.flat_map(mapper),
        ops.filter(predicate),
    )


__all__ = ["buffer_", "buffer_with_count_", "buffer_when_", "buffer_toggle_"]
