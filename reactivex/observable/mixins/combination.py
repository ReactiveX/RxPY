"""Combination operators mixin for Observable."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:
    from asyncio import Future

    from reactivex.observable import Observable


_T = TypeVar("_T", covariant=True)


class CombinationMixin(Generic[_T]):
    """Mixin providing combination operators for Observable.

    This mixin adds operators that combine multiple observable sequences,
    including merge, concat, zip, and various other combination strategies.
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

    def merge(
        self, *sources: Observable[_T], max_concurrent: int | None = None
    ) -> Observable[_T]:
        """Merge with other observables.

        Merges an observable sequence of observable sequences into an observable
        sequence, limiting the number of concurrent subscriptions to inner sequences.

        Examples:
            Fluent style:
            >>> result = source.merge(other1, other2)
            >>> result = source.merge(other, max_concurrent=2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.merge(other1, other2))

        Args:
            *sources: Observable sequences to merge with the source.
            max_concurrent: Maximum number of concurrent subscriptions.

        Returns:
            The observable sequence that merges the elements of the observable
            sequences.

        See Also:
            - :func:`merge <reactivex.operators.merge>`
            - :meth:`concat`
            - :meth:`combine_latest`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.merge(*sources, max_concurrent=max_concurrent)
        )

    def concat(self, *sources: Observable[_T]) -> Observable[_T]:
        """Concatenate with other observables.

        Concatenates all the observable sequences.

        Examples:
            Fluent style:
            >>> result = source.concat(other1, other2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.concat(other1, other2))

        Args:
            *sources: Observable sequences to concatenate with the source.

        Returns:
            An observable sequence that contains the elements of each given
            sequence, in sequential order.

        See Also:
            - :func:`concat <reactivex.operators.concat>`
            - :meth:`merge`
            - :meth:`concat_map`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.concat(*sources))

    def zip(self, *sources: Observable[Any]) -> Observable[Any]:
        """Zip with other observables.

        Merges the specified observable sequences into one observable sequence
        by creating a tuple whenever all of the observable sequences have
        produced an element at a corresponding index.

        Examples:
            Fluent style:
            >>> result = source.zip(other1, other2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.zip(other1, other2))

        Args:
            *sources: Observable sequences to zip with the source.

        Returns:
            An observable sequence containing the result of combining elements
            of the sources as tuples.

        See Also:
            - :func:`zip <reactivex.operators.zip>`
            - :meth:`combine_latest`
            - :meth:`with_latest_from`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.zip(*sources))

    def combine_latest(self, *sources: Observable[Any]) -> Observable[Any]:
        """Combine latest values from observables.

        Merges the specified observable sequences into one observable sequence
        by creating a tuple whenever any of the observable sequences produces
        an element.

        Examples:
            Fluent style:
            >>> result = source.combine_latest(other1, other2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.combine_latest(other1, other2))

        Args:
            *sources: Observable sequences to combine with the source.

        Returns:
            An observable sequence containing the result of combining elements
            of the sources as tuples.

        See Also:
            - :func:`combine_latest <reactivex.operators.combine_latest>`
            - :meth:`zip`
            - :meth:`with_latest_from`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.combine_latest(*sources))

    def with_latest_from(self, *sources: Observable[Any]) -> Observable[Any]:
        """Combine with latest values from other observables.

        Merges the specified observable sequences into one observable sequence
        by creating a tuple only when the first observable sequence (self)
        produces an element.

        Examples:
            Fluent style:
            >>> result = source.with_latest_from(other1, other2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.with_latest_from(other1, other2))

        Args:
            *sources: Observable sequences whose latest values to include.

        Returns:
            An observable sequence containing the result of combining the source
            with the latest values from other sources as tuples.

        See Also:
            - :func:`with_latest_from <reactivex.operators.with_latest_from>`
            - :meth:`combine_latest`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.with_latest_from(*sources))

    def start_with(self, *args: Any) -> Observable[Any]:
        """Prepend values to the sequence.

        Prepends a sequence of values to an observable sequence.

        Examples:
            Fluent style:
            >>> result = source.start_with(1, 2, 3)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.start_with(1, 2, 3))

        Args:
            *args: Values to prepend to the observable sequence.

        Returns:
            The source sequence prepended with the specified values.

        See Also:
            - :func:`start_with <reactivex.operators.start_with>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.start_with(*args))

    def fork_join(self, *others: Observable[Any]) -> Observable[tuple[Any, ...]]:
        """Wait for all observables to complete and combine last values.

        Wait for observables to complete and then combine last values
        they emitted into a tuple. Whenever any of those observables
        completes without emitting any value, result sequence will
        complete at that moment as well.

        Examples:
            Fluent style:
            >>> result = source.fork_join(observable2, observable3)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.fork_join(observable2, observable3))

        Args:
            *others: Other observable sequences to combine with.

        Returns:
            An observable sequence containing a tuple with the last elements
            from all sequences.

        See Also:
            - :func:`fork_join <reactivex.operators.fork_join>`
            - :meth:`zip`
            - :meth:`combine_latest`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.fork_join(*others))

    def switch_latest(self) -> Observable[Any]:
        """Switch to the most recent inner observable.

        Transforms an observable sequence of observable sequences into an
        observable sequence producing values only from the most recent
        observable sequence.

        Examples:
            Fluent style:
            >>> result = source_of_observables.switch_latest()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.switch_latest())

        Returns:
            The observable sequence that at any point in time produces the
            elements of the most recent inner observable sequence that has
            been received.

        See Also:
            - :func:`switch_latest <reactivex.operators.switch_latest>`
            - :meth:`switch_map`
            - :meth:`merge`
        """
        # Cast is safe: switch_latest is meant to be called on Observable
        # of Observables. The fluent API allows chaining this on nested
        # observable sequences. The cast preserves type safety for the
        # intended use case where _T is an Observable or Future.

        from reactivex import operators as ops

        source: Observable[Observable[Any] | Future[Any]] = cast(
            "Observable[Observable[Any] | Future[Any]]", self._as_observable()
        )
        return ops.switch_latest()(source)

    def amb(self, right_source: Observable[_T]) -> Observable[_T]:
        """Propagate the observable that reacts first.

        Propagates the observable sequence that reacts first.

        Examples:
            Fluent style:
            >>> result = source1.amb(source2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source1.pipe(ops.amb(source2))

        Args:
            right_source: Second observable sequence.

        Returns:
            An observable sequence that surfaces any of the given sequences,
            whichever reacted first.

        See Also:
            - :func:`amb <reactivex.operators.amb>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.amb(right_source))
