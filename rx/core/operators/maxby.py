from typing import Callable, Optional
from rx.core import Observable
from rx.core.typing import Mapper, SubComparer
from rx.internal.basic import default_sub_comparer

from .minby import extrema_by


def _max_by(key_mapper: Mapper,
            comparer: Optional[SubComparer] = None
            ) -> Callable[[Observable], Observable]:

    cmp = comparer or default_sub_comparer

    def max_by(source: Observable) -> Observable:
        """Partially applied max_by operator.

        Returns the elements in an observable sequence with the maximum
        key value.

        Examples:
            >>> res = max_by(source)

        Args:
            source: The source observable sequence to.

        Returns:
            An observable sequence containing a list of zero or more
            elements that have a maximum key value.
        """
        return extrema_by(source, key_mapper, cmp)
    return max_by
