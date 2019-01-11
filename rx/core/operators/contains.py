from typing import Any, Callable

from rx import operators as ops
from rx.core import Observable
from rx.internal.basic import default_comparer


def _contains(value: Any, comparer=None) -> Callable[[Observable], Observable]:
    comparer_ = comparer or default_comparer

    filtering = ops.filter(lambda v: comparer_(v, value))
    something = ops.some()

    def contains(source: Observable) -> Observable:
        """Determines whether an observable sequence contains a specified
        element with an optional equality comparer.

        Examples:
            >>> res = contains(sournce)

        Args:
            source: The source observable to compare.

        Returns:
            An observable sequence containing a single element
            determining whether the source sequence contains an element
            that has the specified value.
        """

        return source.pipe(
            filtering,
            something
        )
    return contains
