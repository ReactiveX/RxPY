from collections.abc import Callable
from typing import TypeVar

from reactivex import Observable, typing
from reactivex.internal.basic import default_sub_comparer

from ._minby import extrema_by

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")


def max_by_(
    key_mapper: typing.Mapper[_T, _TKey],
    comparer: typing.SubComparer[_TKey] | None = None,
) -> Callable[[Observable[_T]], Observable[list[_T]]]:
    cmp = comparer or default_sub_comparer

    def max_by(source: Observable[_T]) -> Observable[list[_T]]:
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


__all__ = ["max_by_"]
