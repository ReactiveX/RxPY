from typing import Any, Callable, Optional, TypeVar

from reactivex import Observable, operators
from reactivex.typing import Predicate

from ._lastordefault import last_or_default_async

_T = TypeVar("_T")


def last_(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[Any]]:
    def last(source: Observable[_T]) -> Observable[Any]:
        """Partially applied last operator.

        Returns the last element of an observable sequence that
        satisfies the condition in the predicate if specified, else
        the last element.

        Examples:
            >>> res = last(source)

        Args:
            source: Source observable to get last item from.

        Returns:
            An observable sequence containing the last element in the
            observable sequence that satisfies the condition in the
            predicate.
        """

        if predicate:
            return source.pipe(
                operators.filter(predicate),
                operators.last(),
            )

        return last_or_default_async(source, False)

    return last


__all__ = ["last_"]
