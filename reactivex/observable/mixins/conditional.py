"""Conditional operators mixin for Observable."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

if TYPE_CHECKING:
    from reactivex.observable import Observable


_T = TypeVar("_T", covariant=True)
_A = TypeVar("_A")


class ConditionalMixin(Generic[_T]):
    """Mixin providing conditional operators for Observable.

    This mixin adds operators that conditionally process or emit elements
    based on various conditions.
    """

    def _as_observable(self) -> Observable[_T]:
        """Cast mixin instance to Observable preserving type parameter.

        This is safe because this mixin is only ever used as part of the Observable
        class through multiple inheritance. At runtime, `self` in mixin methods will
        always be an Observable[_T] instance. The type checker cannot infer this
        because it analyzes mixins in isolation.

        Returns:
            The instance cast to Observable[_T] for type-safe method access.
        """
        return cast("Observable[_T]", self)

    @overload
    def default_if_empty(self, default_value: _A) -> Observable[_T | _A]: ...

    @overload
    def default_if_empty(self) -> Observable[_T | None]: ...

    def default_if_empty(self, default_value: Any = None) -> Observable[Any]:
        """Return default value if observable is empty.

        Returns the elements of the specified sequence or the specified value in
        a singleton sequence if the sequence is empty.

        Examples:
            Fluent style:
            >>> result = source.default_if_empty(42)
            >>> result = source.default_if_empty()  # Defaults to None

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.default_if_empty(42))

        Args:
            default_value: The value to return if the sequence is empty.

        Returns:
            An observable sequence that contains the specified default value if
            the source is empty; otherwise, the elements of the source.

        See Also:
            - :func:`default_if_empty <reactivex.operators.default_if_empty>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.default_if_empty(default_value))

    def find(
        self, predicate: Callable[[_T, int, Observable[_T]], bool]
    ) -> Observable[_T | None]:
        """Find first element matching predicate.

        Searches for an element that matches the conditions defined by the
        specified predicate, and returns the first occurrence within the entire
        Observable sequence.

        Examples:
            Fluent style:
            >>> result = source.find(lambda x, i, obs: x > 3)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.find(lambda x, i, obs: x > 3))

        Args:
            predicate: The predicate that defines the conditions of the element to
                search for. Takes (value, index, source).

        Returns:
            An observable sequence with the first element that matches the conditions
            defined by the specified predicate, if found; otherwise, None.

        See Also:
            - :func:`find <reactivex.operators.find>`
            - :meth:`find_index`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.find(predicate))

    def find_index(
        self, predicate: Callable[[_T, int, Observable[_T]], bool]
    ) -> Observable[int | None]:
        """Find index of first element matching predicate.

        Searches for an element that matches the conditions defined by the specified
        predicate, and returns an Observable sequence with the zero-based index of
        the first occurrence within the entire Observable sequence.

        Examples:
            Fluent style:
            >>> result = source.find_index(lambda x, i, obs: x > 3)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.find_index(lambda x, i, obs: x > 3))

        Args:
            predicate: The predicate that defines the conditions of the element to
                search for. Takes (value, index, source).

        Returns:
            An observable sequence with the zero-based index of the first element
            that matches the conditions; if not found, returns -1.

        See Also:
            - :func:`find_index <reactivex.operators.find_index>`
            - :meth:`find`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.find_index(predicate))
