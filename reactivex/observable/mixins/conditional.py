"""Conditional operators mixin for Observable."""

from __future__ import annotations

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
