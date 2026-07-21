"""Testing operators mixin for Observable."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from reactivex import typing

if TYPE_CHECKING:
    from reactivex.observable import Observable

_T = TypeVar("_T", covariant=True)


class TestingMixin(Generic[_T]):
    """Mixin providing testing operators for Observable.

    This mixin adds operators that test properties of observable sequences,
    including checking conditions, emptiness, and equality.
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

    def all(self, predicate: typing.Predicate[_T]) -> Observable[bool]:
        """Check if all elements satisfy a condition.

        Determines whether all elements of an observable sequence satisfy
        a condition.

        Examples:
            Fluent style:
            >>> result = source.all(lambda x: x > 0)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.all(lambda x: x > 0))

        Args:
            predicate: A function to test each element for a condition.

        Returns:
            An observable sequence containing a single boolean value
            indicating whether all elements in the source sequence pass
            the test in the specified predicate.

        See Also:
            - :func:`all <reactivex.operators.all>`
            - :meth:`some`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.all(predicate))

    def some(self, predicate: typing.Predicate[_T] | None = None) -> Observable[bool]:
        """Check if some elements satisfy a condition.

        Determines whether some element of an observable sequence satisfies
        a condition if present, else if some items are in the sequence.

        Examples:
            Fluent style:
            >>> result = source.some(lambda x: x > 10)
            >>> result = source.some()  # Check if sequence is not empty

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.some(lambda x: x > 10))

        Args:
            predicate: A function to test each element for a condition.
                If not specified, checks if the sequence contains any elements.

        Returns:
            An observable sequence containing a single boolean value
            indicating whether at least one element in the source sequence
            passes the test (or whether the sequence is non-empty if no
            predicate is specified).

        See Also:
            - :func:`some <reactivex.operators.some>`
            - :meth:`all`
            - :meth:`is_empty`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.some(predicate))

    def is_empty(self) -> Observable[bool]:
        """Check if the sequence is empty.

        Determines whether an observable sequence is empty.

        Examples:
            Fluent style:
            >>> result = source.is_empty()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.is_empty())

        Returns:
            An observable sequence containing a single boolean value
            indicating whether the source sequence is empty.

        See Also:
            - :func:`is_empty <reactivex.operators.is_empty>`
            - :meth:`some`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.is_empty())

    def contains(
        self, value: Any, comparer: typing.Comparer[Any] | None = None
    ) -> Observable[bool]:
        """Check if the sequence contains a value.

        Determines whether an observable sequence contains a specified
        element with an optional equality comparer.

        Examples:
            Fluent style:
            >>> result = source.contains(42)
            >>> result = source.contains("hello", lambda a, b: a.lower() == b.lower())

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.contains(42))

        Args:
            value: The value to locate in the source sequence.
            comparer: An equality comparer to compare elements.

        Returns:
            An observable sequence containing a single boolean value
            indicating whether the source sequence contains an element
            that has the specified value.

        See Also:
            - :func:`contains <reactivex.operators.contains>`
            - :meth:`some`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.contains(value, comparer))

    def sequence_equal(
        self,
        second: Observable[_T] | Iterable[_T],
        comparer: typing.Comparer[_T] | None = None,
    ) -> Observable[bool]:
        """Check if two sequences are equal.

        Determines whether two sequences are equal by comparing the
        elements pairwise using a specified equality comparer.

        Examples:
            Fluent style:
            >>> result = source.sequence_equal(other_observable)
            >>> result = source.sequence_equal([1, 2, 3])

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.sequence_equal(other_observable))

        Args:
            second: Second observable sequence or iterable to compare.
            comparer: Comparer used to compare elements of both sequences.

        Returns:
            An observable sequence that contains a single boolean value
            which indicates whether both sequences are of equal length and
            their corresponding elements are equal according to the
            specified comparer.

        See Also:
            - :func:`sequence_equal <reactivex.operators.sequence_equal>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.sequence_equal(second, comparer))
