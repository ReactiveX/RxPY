from typing import Any, Callable

import rx

from rx.core import Observable


def _start_with(*args: Any) -> Callable[[Observable], Observable]:
    def start_with(source: Observable) -> Observable:
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
