"""Filtering operators mixin for Observable."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from reactivex import typing

if TYPE_CHECKING:
    from reactivex.observable import Observable

_T = TypeVar("_T", covariant=True)


class FilteringMixin(Generic[_T]):
    """Mixin providing filtering operators for Observable.

    This mixin adds operators that filter elements based on various criteria,
    including predicates, position, distinctness, and timing.
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

    def filter(self, predicate: typing.Predicate[Any]) -> Observable[Any]:
        """Filter elements based on a predicate.

        Filters the elements of an observable sequence based on a predicate function.
        Only elements for which the predicate returns True will be emitted.

        Examples:
            Fluent style:
            >>> result = source.filter(lambda x: x > 0)
            >>> result = source.filter(lambda x: x % 2 == 0)  # Even numbers only

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.filter(lambda x: x > 0))

        Args:
            predicate: A function to test each source element for a condition.

        Returns:
            An observable sequence that contains elements from the input sequence
            that satisfy the condition specified by the predicate.

        See Also:
            - :func:`filter <reactivex.operators.filter>`
            - :meth:`filter_indexed`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.filter(predicate))

    def take(self, count: int) -> Observable[Any]:
        """Return a specified number of contiguous elements from the start.

        Takes the first `count` elements from the observable sequence and ignores
        the rest.

        Examples:
            Fluent style:
            >>> result = source.take(5)
            >>> result = source.take(3).map(lambda x: x * 2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.take(5))

        Args:
            count: The number of elements to return.

        Returns:
            An observable sequence that contains the specified number of elements
            from the start of the input sequence.

        See Also:
            - :func:`take <reactivex.operators.take>`
            - :meth:`take_last`
            - :meth:`take_while`
            - :meth:`skip`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.take(count))

    def skip(self, count: int) -> Observable[Any]:
        """Skip a specified number of elements from the start.

        Bypasses the first `count` elements in the observable sequence and returns
        the remaining elements.

        Examples:
            Fluent style:
            >>> result = source.skip(5)
            >>> result = source.skip(2).take(10)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.skip(5))

        Args:
            count: The number of elements to skip before returning elements.

        Returns:
            An observable sequence that contains the elements that occur after
            the specified index in the input sequence.

        See Also:
            - :func:`skip <reactivex.operators.skip>`
            - :meth:`skip_last`
            - :meth:`skip_while`
            - :meth:`take`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.skip(count))

    def first(self, predicate: typing.Predicate[Any] | None = None) -> Observable[Any]:
        """Return the first element, optionally that satisfies a condition.

        Returns the first element of an observable sequence that satisfies the
        condition in the predicate if present, otherwise the first element.

        Examples:
            Fluent style:
            >>> result = source.first()
            >>> result = source.first(lambda x: x > 10)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.first())
            >>> result = source.pipe(ops.first(lambda x: x > 10))

        Args:
            predicate: An optional function to test each source element for a condition.

        Returns:
            An observable sequence containing the first element that satisfies the
            condition if predicate is provided, otherwise the first element.

        Raises:
            SequenceContainsNoElementsError: if the source sequence is empty.

        See Also:
            - :func:`first <reactivex.operators.first>`
            - :meth:`first_or_default`
            - :meth:`last`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.first(predicate))

    def last(self, predicate: typing.Predicate[Any] | None = None) -> Observable[Any]:
        """Return the last element, optionally that satisfies a condition.

        Returns the last element of an observable sequence that satisfies the
        condition in the predicate if specified, otherwise the last element.

        Examples:
            Fluent style:
            >>> result = source.last()
            >>> result = source.last(lambda x: x < 10)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.last())
            >>> result = source.pipe(ops.last(lambda x: x < 10))

        Args:
            predicate: An optional function to test each source element for a condition.

        Returns:
            An observable sequence containing the last element that satisfies the
            condition if predicate is provided, otherwise the last element.

        Raises:
            SequenceContainsNoElementsError: if the source sequence is empty.

        See Also:
            - :func:`last <reactivex.operators.last>`
            - :meth:`last_or_default`
            - :meth:`first`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.last(predicate))

    def take_last(self, count: int) -> Observable[Any]:
        """Take a specified number of elements from the end.

        Returns a specified number of contiguous elements from the end of an
        observable sequence.

        Examples:
            Fluent style:
            >>> result = source.take_last(3)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.take_last(3))

        Args:
            count: Number of elements to take from the end of the sequence.

        Returns:
            An observable sequence containing the specified number of elements
            from the end of the source sequence.

        See Also:
            - :func:`take_last <reactivex.operators.take_last>`
            - :meth:`take`
            - :meth:`skip_last`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.take_last(count))

    def skip_last(self, count: int) -> Observable[Any]:
        """Skip a specified number of elements from the end.

        Bypasses a specified number of elements at the end of an observable
        sequence.

        Examples:
            Fluent style:
            >>> result = source.skip_last(2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.skip_last(2))

        Args:
            count: Number of elements to bypass at the end of the sequence.

        Returns:
            An observable sequence containing the source sequence elements except
            for the bypassed ones at the end.

        See Also:
            - :func:`skip_last <reactivex.operators.skip_last>`
            - :meth:`skip`
            - :meth:`take_last`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.skip_last(count))

    def distinct(
        self,
        key_mapper: typing.Mapper[Any, Any] | None = None,
        comparer: typing.Comparer[Any] | None = None,
    ) -> Observable[Any]:
        """Return distinct elements based on a key selector and comparer.

        Returns an observable sequence that contains only distinct elements according
        to the key_mapper and the comparer.

        Examples:
            Fluent style:
            >>> result = source.distinct()
            >>> result = source.distinct(lambda x: x.id)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.distinct())

        Args:
            key_mapper: Optional function to compute a comparison key for each element.
            comparer: Optional equality comparer for computed keys.

        Returns:
            An observable sequence only containing the distinct elements from
            the source sequence.

        See Also:
            - :func:`distinct <reactivex.operators.distinct>`
            - :meth:`distinct_until_changed`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.distinct(key_mapper, comparer))

    def distinct_until_changed(
        self,
        key_mapper: typing.Mapper[Any, Any] | None = None,
        comparer: typing.Comparer[Any] | None = None,
    ) -> Observable[Any]:
        """Return elements with distinct contiguous values.

        Returns an observable sequence that contains only distinct contiguous
        elements according to the key_mapper and the comparer.

        Examples:
            Fluent style:
            >>> result = source.distinct_until_changed()
            >>> result = source.distinct_until_changed(lambda x: x.id)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.distinct_until_changed())

        Args:
            key_mapper: Optional function to compute a comparison key for each element.
            comparer: Optional equality comparer for computed keys.

        Returns:
            An observable sequence only containing distinct contiguous elements from
            the source sequence.

        See Also:
            - :func:`distinct_until_changed \
<reactivex.operators.distinct_until_changed>`
            - :meth:`distinct`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.distinct_until_changed(key_mapper, comparer)
        )

    def take_while(
        self, predicate: typing.Predicate[Any], inclusive: bool = False
    ) -> Observable[Any]:
        """Take elements while predicate is true.

        Returns elements from an observable sequence as long as a specified
        condition is true.

        Examples:
            Fluent style:
            >>> result = source.take_while(lambda x: x < 5)
            >>> result = source.take_while(lambda x: x < 5, inclusive=True)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.take_while(lambda x: x < 5))

        Args:
            predicate: A function to test each element for a condition.
            inclusive: If True, include the element that failed the predicate.

        Returns:
            An observable sequence that contains elements from the input sequence
            that occur before the element at which the test no longer passes.

        See Also:
            - :func:`take_while <reactivex.operators.take_while>`
            - :meth:`skip_while`
            - :meth:`take_until`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.take_while(predicate, inclusive))

    def skip_while(self, predicate: typing.Predicate[Any]) -> Observable[Any]:
        """Skip elements while predicate is true.

        Bypasses elements in an observable sequence as long as a specified
        condition is true and then returns the remaining elements.

        Examples:
            Fluent style:
            >>> result = source.skip_while(lambda x: x < 5)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.skip_while(lambda x: x < 5))

        Args:
            predicate: A function to test each element for a condition.

        Returns:
            An observable sequence that contains the elements from the input
            sequence starting at the first element in the linear series that
            does not pass the test specified by predicate.

        See Also:
            - :func:`skip_while <reactivex.operators.skip_while>`
            - :meth:`take_while`
            - :meth:`skip_until`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.skip_while(predicate))

    def take_until(self, other: Observable[Any]) -> Observable[Any]:
        """Take elements until other observable emits.

        Returns the values from the source observable sequence until the other
        observable sequence produces a value.

        Examples:
            Fluent style:
            >>> result = source.take_until(trigger)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.take_until(trigger))

        Args:
            other: Observable sequence that terminates propagation of elements
                of the source sequence.

        Returns:
            An observable sequence containing the elements of the source sequence
            up to the point the other sequence interrupted further propagation.

        See Also:
            - :func:`take_until <reactivex.operators.take_until>`
            - :meth:`skip_until`
            - :meth:`take_while`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.take_until(other))

    def skip_until(self, other: Observable[Any]) -> Observable[Any]:
        """Skip elements until other observable emits.

        Returns the values from the source observable sequence only after the
        other observable sequence produces a value.

        Examples:
            Fluent style:
            >>> result = source.skip_until(trigger)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.skip_until(trigger))

        Args:
            other: The observable sequence that triggers propagation of elements
                of the source sequence.

        Returns:
            An observable sequence containing the elements of the source sequence
            starting from the point the other sequence triggered propagation.

        See Also:
            - :func:`skip_until <reactivex.operators.skip_until>`
            - :meth:`take_until`
            - :meth:`skip_while`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.skip_until(other))

    def element_at(self, index: int) -> Observable[Any]:
        """Get the element at a specified index.

        Returns the element at a specified index in a sequence.

        Examples:
            Fluent style:
            >>> result = source.element_at(5)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.element_at(5))

        Args:
            index: The zero-based index of the element to retrieve.

        Returns:
            An observable sequence that produces the element at the specified
            position in the source sequence.

        Raises:
            ArgumentOutOfRangeError: if index is less than 0 or greater than
            or equal to the number of elements in the source sequence.

        See Also:
            - :func:`element_at <reactivex.operators.element_at>`
            - :meth:`element_at_or_default`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.element_at(index))

    def filter_indexed(
        self, predicate_indexed: typing.PredicateIndexed[Any]
    ) -> Observable[Any]:
        """Filter elements based on a predicate with index.

        Filters the elements of an observable sequence based on a predicate function
        that incorporates the element's index.

        Examples:
            Fluent style:
            >>> result = source.filter_indexed(lambda x, i: i % 2 == 0)  # Even indices
            >>> result = source.filter_indexed(lambda x, i: x > i)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.filter_indexed(lambda x, i: i % 2 == 0))

        Args:
            predicate_indexed: A function to test each source element and its index.
                The function receives (value, index) and returns bool.

        Returns:
            An observable sequence that contains elements from the input sequence
            that satisfy the condition specified by the indexed predicate.

        See Also:
            - :func:`filter_indexed <reactivex.operators.filter_indexed>`
            - :meth:`filter`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.filter_indexed(predicate_indexed))

    def take_while_indexed(
        self, predicate_indexed: typing.PredicateIndexed[Any], inclusive: bool = False
    ) -> Observable[Any]:
        """Take elements while predicate is true, with index.

        Returns elements from an observable sequence as long as a specified
        condition is true, incorporating the element's index.

        Examples:
            Fluent style:
            >>> result = source.take_while_indexed(lambda x, i: i < 5)
            >>> result = source.take_while_indexed(
            ...     lambda x, i: x < i * 10, inclusive=True
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.take_while_indexed(lambda x, i: i < 5))

        Args:
            predicate_indexed: A function to test each element and its index.
            inclusive: If True, include the element that failed the predicate.

        Returns:
            An observable sequence that contains elements from the input sequence
            that occur before the element at which the test no longer passes.

        See Also:
            - :func:`take_while_indexed <reactivex.operators.take_while_indexed>`
            - :meth:`take_while`
            - :meth:`skip_while_indexed`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.take_while_indexed(predicate_indexed, inclusive)
        )

    def skip_while_indexed(
        self, predicate_indexed: typing.PredicateIndexed[Any]
    ) -> Observable[Any]:
        """Skip elements while predicate is true, with index.

        Bypasses elements in an observable sequence as long as a specified
        condition is true and then returns the remaining elements, incorporating
        the element's index.

        Examples:
            Fluent style:
            >>> result = source.skip_while_indexed(lambda x, i: i < 3)
            >>> result = source.skip_while_indexed(lambda x, i: x < i * 10)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.skip_while_indexed(lambda x, i: i < 3))

        Args:
            predicate_indexed: A function to test each element and its index.

        Returns:
            An observable sequence that contains the elements from the input
            sequence starting at the first element in the linear series that
            does not pass the test specified by predicate.

        See Also:
            - :func:`skip_while_indexed <reactivex.operators.skip_while_indexed>`
            - :meth:`skip_while`
            - :meth:`take_while_indexed`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.skip_while_indexed(predicate_indexed))

    def single(self, predicate: typing.Predicate[_T] | None = None) -> Observable[_T]:
        """Return single element matching predicate.

        Returns the only element of an observable sequence that satisfies the condition
        in the optional predicate, and reports an exception if there is not exactly one
        element in the observable sequence.

        Examples:
            Fluent style:
            >>> result = source.single()
            >>> result = source.single(lambda x: x == 42)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.single())
            >>> result = source.pipe(ops.single(lambda x: x == 42))

        Args:
            predicate: A predicate function to evaluate for elements in the source
                sequence.

        Returns:
            An observable sequence containing the single element in the observable
            sequence that satisfies the condition in the predicate.

        Raises:
            Exception: If there is not exactly one element matching the predicate.

        See Also:
            - :func:`single <reactivex.operators.single>`
            - :meth:`single_or_default`
            - :meth:`first`
            - :meth:`last`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.single(predicate))

    def single_or_default(
        self, predicate: typing.Predicate[_T] | None = None, default_value: Any = None
    ) -> Observable[_T]:
        """Return single element or default.

        Returns the only element of an observable sequence that matches the predicate,
        or a default value if no such element exists.

        Examples:
            Fluent style:
            >>> result = source.single_or_default()
            >>> result = source.single_or_default(lambda x: x == 42, 0)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.single_or_default())
            >>> result = source.pipe(ops.single_or_default(lambda x: x == 42, 0))

        Args:
            predicate: A predicate function to evaluate for elements in the source
                sequence.
            default_value: The default value if no element matches or sequence is empty.

        Returns:
            An observable sequence containing the single element in the observable
            sequence that satisfies the condition in the predicate, or the default
            value if no such element exists.

        See Also:
            - :func:`single_or_default <reactivex.operators.single_or_default>`
            - :meth:`single`
            - :meth:`first_or_default`
            - :meth:`last_or_default`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.single_or_default(predicate, default_value)
        )

    def element_at_or_default(
        self, index: int, default_value: _T | None = None
    ) -> Observable[_T]:
        """Get element at index or default.

        Returns the element at a specified index in a sequence or a default value if
        the index is out of range.

        Examples:
            Fluent style:
            >>> result = source.element_at_or_default(5)
            >>> result = source.element_at_or_default(5, 0)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.element_at_or_default(5))
            >>> result = source.pipe(ops.element_at_or_default(5, 0))

        Args:
            index: The zero-based index of the element to retrieve.
            default_value: The default value if the index is outside the bounds of
                the source sequence.

        Returns:
            An observable sequence that produces the element at the specified position
            in the source sequence, or a default value if the index is outside the
            bounds of the source sequence.

        See Also:
            - :func:`element_at_or_default <reactivex.operators.element_at_or_default>`
            - :meth:`element_at`
            - :meth:`first_or_default`
            - :meth:`last_or_default`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.element_at_or_default(index, default_value)
        )
