from typing import Callable, TypeVar

import rx
from rx.core import Observable

_T = TypeVar("_T")


def start_with_(*args: _T) -> Callable[[Observable[_T]], Observable[_T]]:
    def start_with(source: Observable[_T]) -> Observable[_T]:
        """Partially applied start_with operator.

        Prepends a sequence of values to an observable sequence.

        Example:
            >>> start_with(source)

        Returns:
            The source sequence prepended with the specified values.
        """
        start = rx.from_iterable(args)
        sequence = [start, source]
        return rx.concat(*sequence)

    return start_with


__all__ = ["start_with_"]
