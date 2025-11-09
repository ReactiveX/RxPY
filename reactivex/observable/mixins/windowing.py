"""Windowing operators mixin for Observable."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from reactivex import typing

if TYPE_CHECKING:
    from reactivex.observable import Observable


_T = TypeVar("_T", covariant=True)
_A = TypeVar("_A")
_B = TypeVar("_B")


class WindowingMixin(Generic[_T]):
    """Mixin providing windowing operators for Observable.

    This mixin adds operators that group and window elements,
    including buffering, grouping, partitioning, and pairing.
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

    def buffer(self, boundaries: Observable[Any]) -> Observable[list[_T]]:
        """Buffer elements based on boundary observable.

        Projects each element of an observable sequence into zero or more buffers
        which are produced based on timing information from another observable sequence.

        Examples:
            Fluent style:
            >>> result = source.buffer(rx.interval(1.0))
            >>> result = source.buffer(trigger_observable)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.buffer(rx.interval(1.0)))

        Args:
            boundaries: Observable sequence whose elements denote the creation
                and completion of buffers.

        Returns:
            An observable sequence of buffers.

        See Also:
            - :func:`buffer <reactivex.operators.buffer>`
            - :meth:`buffer_with_count`
            - :meth:`buffer_with_time`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.buffer(boundaries))

    def group_by(
        self,
        key_mapper: typing.Mapper[_T, Any],
        element_mapper: typing.Mapper[_T, Any] | None = None,
        subject_mapper: Callable[[], Any] | None = None,
    ) -> Observable[Any]:
        """Group elements by key.

        Groups the elements of an observable sequence according to a
        specified key mapper function and comparer and selects the
        resulting elements by using a specified function.

        Examples:
            Fluent style:
            >>> result = source.group_by(lambda x: x % 2)
            >>> result = source.group_by(
            ...     key_mapper=lambda x: x.category,
            ...     element_mapper=lambda x: x.value
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.group_by(lambda x: x % 2))

        Args:
            key_mapper: A function to extract the key for each element.
            element_mapper: A function to map each source element to an
                element in an observable group.
            subject_mapper: A function that returns a subject to use for
                each group.

        Returns:
            A sequence of observable groups, each of which corresponds to
            a unique key value, containing all elements that share that
            same key value.

        See Also:
            - :func:`group_by <reactivex.operators.group_by>`
            - :meth:`partition`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.group_by(key_mapper, element_mapper, subject_mapper)
        )

    def partition(self, predicate: typing.Predicate[_T]) -> list[Observable[_T]]:
        """Partition elements into two sequences.

        Returns two observables which partition the observations of the
        source by the given function. The first will trigger observations
        for those values for which the predicate returns true. The second
        will trigger observations for those values where the predicate
        returns false.

        Examples:
            Fluent style:
            >>> evens, odds = source.partition(lambda x: x % 2 == 0)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> evens, odds = source.pipe(ops.partition(lambda x: x % 2 == 0))

        Args:
            predicate: The function to test each source element for a condition.

        Returns:
            A list of two observable sequences. The first sequence emits
            elements for which the predicate returned true; the second
            emits those for which it returned false.

        See Also:
            - :func:`partition <reactivex.operators.partition>`
            - :meth:`filter`
            - :meth:`group_by`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.partition(predicate))

    def pairwise(self) -> Observable[tuple[_T, _T]]:
        """Emit consecutive pairs of elements.

        Returns a new observable that triggers on the second and subsequent
        triggerings of the input observable. The Nth triggering of the
        input observable passes the arguments from the N-1th and Nth
        triggering as a pair.

        Examples:
            Fluent style:
            >>> result = source.pairwise()
            >>> # Input: 1, 2, 3, 4
            >>> # Output: (1, 2), (2, 3), (3, 4)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.pairwise())

        Returns:
            An observable that triggers on successive pairs of
            observations from the input observable as tuples.

        See Also:
            - :func:`pairwise <reactivex.operators.pairwise>`
            - :meth:`buffer`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.pairwise())

    def partition_indexed(
        self, predicate_indexed: typing.PredicateIndexed[_T]
    ) -> list[Observable[_T]]:
        """Partition observable into two based on indexed predicate.

        Returns a list of two observable sequences: the first contains elements
        for which the predicate evaluated true, the second contains the rest.
        The predicate function incorporates the element's index.

        Examples:
            Fluent style:
            >>> true_obs, false_obs = source.partition_indexed(lambda x, i: i % 2 == 0)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> true_obs, false_obs = source.pipe(
            ...     ops.partition_indexed(lambda x, i: i % 2 == 0)
            ... )

        Args:
            predicate_indexed: A function to test each element and its index.
                The function receives (value, index) and returns bool.

        Returns:
            A list of two observables: [true_sequence, false_sequence].

        See Also:
            - :func:`partition_indexed <reactivex.operators.partition_indexed>`
            - :meth:`partition`
            - :meth:`filter_indexed`
        """
        from reactivex import operators as ops

        return ops.partition_indexed(predicate_indexed)(self._as_observable())
