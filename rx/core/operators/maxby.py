from typing import Callable
from rx.core import Observable
from rx.internal.basic import default_sub_comparer

from .minby import extrema_by


def _max_by(key_mapper, comparer=None) -> Callable[[Observable], Observable]:
    comparer = comparer or default_sub_comparer

    def max_by(source: Observable) -> Observable:
        """Partially applied max_by operator.

        Returns the elements in an observable sequence with the maximum
        key value.

        Examples:
            >>> res = max_by(source)

        Args:
            Source: The source observable sequence to.

        Returns:
            An observable sequence containing a list of zero or more
            elements that have a maximum key value.
        """
        return extrema_by(source, key_mapper, comparer)
    return max_by
