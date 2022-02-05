import sys
from typing import Callable, Optional, TypeVar

import rx
from rx.core import Observable
from rx.internal.utils import infinite

_T = TypeVar("_T")


def repeat_(
    repeat_count: Optional[int] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    if repeat_count is None:
        repeat_count = sys.maxsize

    def repeat(source: Observable[_T]) -> Observable[_T]:
        """Repeats the observable sequence a specified number of times.
        If the repeat count is not specified, the sequence repeats
        indefinitely.

        Examples:
            >>> repeated = source.repeat()
            >>> repeated = source.repeat(42)

        Args:
            source: The observable source to repeat.

        Returns:
            The observable sequence producing the elements of the given
            sequence repeatedly.
        """

        if repeat_count is None:
            gen = infinite()
        else:
            gen = range(repeat_count)

        return rx.defer(lambda _: rx.concat_with_iterable(source for _ in gen))

    return repeat


__all = ["repeat"]
