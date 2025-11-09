"""Mathematical operators mixin for Observable."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

from reactivex import typing

if TYPE_CHECKING:
    from reactivex.observable import Observable

_T = TypeVar("_T", covariant=True)


class MathematicalMixin(Generic[_T]):
    """Mixin providing mathematical operators for Observable.

    This mixin adds operators that perform mathematical operations on sequences,
    including counting, summing, averaging, and finding minimum/maximum values.
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

    def count(self, predicate: typing.Predicate[_T] | None = None) -> Observable[int]:
        """Count the number of elements, optionally satisfying a predicate.

        Returns an observable sequence containing a value that represents how many
        elements in the specified observable sequence satisfy a condition if provided,
        else the count of items.

        Examples:
            Fluent style:
            >>> result = source.count()
            >>> result = source.count(lambda x: x > 5)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.count())

        Args:
            predicate: Optional function to test each source element for a condition.

        Returns:
            An observable sequence containing a single element with the number
            of elements in the source sequence that satisfy the condition.

        See Also:
            - :func:`count <reactivex.operators.count>`
            - :meth:`reduce`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.count(predicate))

    @overload
    def sum(self) -> Observable[float]: ...

    @overload
    def sum(self, key_mapper: typing.Mapper[_T, float]) -> Observable[float]: ...

    def sum(
        self, key_mapper: typing.Mapper[Any, float] | None = None
    ) -> Observable[float]:
        """Compute the sum of the sequence.

        Computes the sum of a sequence of values that are obtained by invoking an
        optional transform function on each element of the input sequence, else if
        not specified computes the sum on each item in the sequence.

        Examples:
            Fluent style:
            >>> result = rx.of(1, 2, 3, 4, 5).sum()
            >>> result = source.sum(lambda x: x.value)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.sum())

        Args:
            key_mapper: Optional transform function to apply to each element.

        Returns:
            An observable sequence containing a single element with the sum
            of the values in the source sequence.

        See Also:
            - :func:`sum <reactivex.operators.sum>`
            - :meth:`average`
            - :meth:`reduce`
        """
        from reactivex import operators as ops

        if key_mapper is None:
            # Call operator directly with cast when no key_mapper is provided.
            # sum() expects Observable[float] but we have Observable[_T].
            source: Observable[float] = cast("Observable[float]", self._as_observable())
            return ops.sum()(source)
        return self._as_observable().pipe(ops.sum(key_mapper))

    def average(
        self, key_mapper: typing.Mapper[Any, float] | None = None
    ) -> Observable[float]:
        """Compute the average of the sequence.

        Computes the average of an observable sequence of values that are
        in the sequence or obtained by invoking a transform function on
        each element if present.

        Examples:
            Fluent style:
            >>> result = rx.of(1, 2, 3, 4, 5).average()
            >>> result = source.average(lambda x: x.value)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.average())

        Args:
            key_mapper: Optional transform function to apply to each element.

        Returns:
            An observable sequence containing a single element with the average
            of the sequence of values.

        See Also:
            - :func:`average <reactivex.operators.average>`
            - :meth:`sum`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.average(key_mapper))

    def min(self, comparer: typing.Comparer[_T] | None = None) -> Observable[_T]:
        """Find the minimum element.

        Returns the minimum element in an observable sequence according to the
        optional comparer else a default greater than less than check.

        Examples:
            Fluent style:
            >>> result = source.min()
            >>> result = source.min(lambda x, y: x.value < y.value)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.min())

        Args:
            comparer: Optional comparer function for comparing elements.

        Returns:
            An observable sequence containing a single element with the minimum
            element in the source sequence.

        See Also:
            - :func:`min <reactivex.operators.min>`
            - :meth:`max`
            - :meth:`min_by`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.min(comparer))

    def max(self, comparer: typing.Comparer[_T] | None = None) -> Observable[_T]:
        """Find the maximum element.

        Returns the maximum value in an observable sequence according to the
        specified comparer or default greater than less than check.

        Examples:
            Fluent style:
            >>> result = source.max()
            >>> result = source.max(lambda x, y: x.value > y.value)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.max())

        Args:
            comparer: Optional comparer function for comparing elements.

        Returns:
            An observable sequence containing a single element with the maximum
            element in the source sequence.

        See Also:
            - :func:`max <reactivex.operators.max>`
            - :meth:`min`
            - :meth:`max_by`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.max(comparer))
