from typing import Callable

import rx
from rx.internal.iterable import Iterable as CoreIterable
from rx.core import Observable

def _repeat(repeat_count=None) -> Callable[[Observable], Observable]:
    def repeat(source: Observable) -> Observable:
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
        return rx.defer(lambda _: rx.concat(CoreIterable.repeat(source, repeat_count)))
    return repeat
