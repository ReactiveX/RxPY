"""Simplified curry_flip decorator for RxPY operators.

Adapted from Expression library (https://github.com/dbrattli/Expression)
Simplified to always curry_flip with 1 argument as that's the only case
needed for RxPY operators.
"""

import functools
from collections.abc import Callable
from typing import Concatenate, TypeVar

from typing_extensions import ParamSpec

_P = ParamSpec("_P")
_A = TypeVar("_A")
_B = TypeVar("_B")


def curry_flip(
    fun: Callable[Concatenate[_A, _P], _B],
) -> Callable[_P, Callable[[_A], _B]]:
    """A flipped curry decorator for single-argument currying.

    Makes a function curried, but flips the curried argument to become
    the last argument. This is perfect for RxPY operators where the source
    Observable should be the last argument to enable piping.

    This is a simplified version that always curries exactly 1 argument,
    as that's all RxPY operators need.

    Args:
        fun: The function to curry-flip. Must take at least one argument.

    Returns:
        A curried function where the first argument becomes the last.

    Example:
        >>> @curry_flip
        ... def take(count: int, source: Observable[int]) -> Observable[int]:
        ...     # implementation
        ...     pass
        >>>
        >>> # Now can be used in pipe:
        >>> result = source.pipe(take(5))
        >>> # Or called directly:
        >>> result = take(5)(source)
    """

    @functools.wraps(fun)
    def _wrap_args(*args: _P.args, **kwargs: _P.kwargs) -> Callable[[_A], _B]:
        def _wrap_curried(curry_arg: _A) -> _B:
            return fun(curry_arg, *args, **kwargs)

        return _wrap_curried

    return _wrap_args


__all__ = ["curry_flip"]
