from collections.abc import Callable
from typing import Any, TypeVar

from reactivex import Observable
from reactivex import operators as ops
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def buffer_(
    source: Observable[_T],
    boundaries: Observable[Any],
) -> Observable[list[_T]]:
    """Buffers elements from the source based on boundary notifications.

    Examples:
        >>> res = source.pipe(buffer(boundaries))
        >>> res = buffer(boundaries)(source)

    Args:
        source: Source observable to buffer.
        boundaries: Observable that triggers buffer emissions.

    Returns:
        Observable of lists of buffered elements.
    """
    return source.pipe(
        ops.window(boundaries),
        ops.flat_map(ops.to_list()),
    )


@curry_flip
def buffer_when_(
    source: Observable[_T],
    closing_mapper: Callable[[], Observable[Any]],
) -> Observable[list[_T]]:
    """Buffers elements using a closing mapper function.

    Examples:
        >>> res = source.pipe(buffer_when(lambda: timer(1.0)))
        >>> res = buffer_when(lambda: timer(1.0))(source)

    Args:
        source: Source observable to buffer.
        closing_mapper: Function that returns an observable signaling buffer close.

    Returns:
        Observable of lists of buffered elements.
    """
    return source.pipe(
        ops.window_when(closing_mapper),
        ops.flat_map(ops.to_list()),
    )


@curry_flip
def buffer_toggle_(
    source: Observable[_T],
    openings: Observable[Any],
    closing_mapper: Callable[[Any], Observable[Any]],
) -> Observable[list[_T]]:
    """Buffers elements using opening/closing observables.

    Examples:
        >>> res = source.pipe(buffer_toggle(opens, lambda x: timer(x)))
        >>> res = buffer_toggle(opens, lambda x: timer(x))(source)

    Args:
        source: Source observable to buffer.
        openings: Observable that triggers buffer opening.
        closing_mapper: Function to create closing observable.

    Returns:
        Observable of lists of buffered elements.
    """
    return source.pipe(
        ops.window_toggle(openings, closing_mapper),
        ops.flat_map(ops.to_list()),
    )


@curry_flip
def buffer_with_count_(
    source: Observable[_T],
    count: int,
    skip: int | None = None,
) -> Observable[list[_T]]:
    """Projects each element of an observable sequence into zero or more
    buffers which are produced based on element count information.

    Examples:
        >>> res = source.pipe(buffer_with_count(10))
        >>> res = buffer_with_count(10)(source)
        >>> res = source.pipe(buffer_with_count(10, 1))

    Args:
        source: Source observable to buffer.
        count: Length of each buffer.
        skip: [Optional] Number of elements to skip between
            creation of consecutive buffers. If not provided, defaults to
            the count.

    Returns:
        An observable sequence of buffers.
    """
    skip_ = skip if skip is not None else count

    def mapper(value: Observable[_T]) -> Observable[list[_T]]:
        return value.pipe(
            ops.to_list(),
        )

    def predicate(value: list[_T]) -> bool:
        return len(value) > 0

    return source.pipe(
        ops.window_with_count(count, skip_),
        ops.flat_map(mapper),
        ops.filter(predicate),
    )


__all__ = ["buffer_", "buffer_with_count_", "buffer_when_", "buffer_toggle_"]
