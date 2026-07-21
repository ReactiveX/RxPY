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

    def buffer_with_count(
        self, count: int, skip: int | None = None
    ) -> Observable[list[_T]]:
        """Buffer elements by count.

        Projects each element of an observable sequence into zero or more buffers
        which are produced based on element count information.

        Examples:
            Fluent style:
            >>> result = source.buffer_with_count(5)
            >>> result = source.buffer_with_count(5, 3)  # overlapping buffers

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.buffer_with_count(5))

        Args:
            count: Length of each buffer.
            skip: Number of elements to skip between creation of consecutive
                buffers. If not specified, defaults to count.

        Returns:
            An observable sequence of buffers.

        See Also:
            - :func:`buffer_with_count <reactivex.operators.buffer_with_count>`
            - :meth:`buffer`
            - :meth:`buffer_with_time`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.buffer_with_count(count, skip))

    def buffer_with_time(
        self,
        timespan: typing.RelativeTime,
        timeshift: typing.RelativeTime | None = None,
        scheduler: Any = None,
    ) -> Observable[list[_T]]:
        """Buffer elements by time.

        Projects each element of an observable sequence into zero or more buffers
        which are produced based on timing information.

        Examples:
            Fluent style:
            >>> result = source.buffer_with_time(1.0)
            >>> result = source.buffer_with_time(1.0, 0.5)  # overlapping buffers

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.buffer_with_time(1.0))

        Args:
            timespan: Length of each buffer (in seconds).
            timeshift: Interval between creation of consecutive buffers.
                If not specified, defaults to timespan.
            scheduler: Scheduler to run the timer on. If not specified,
                defaults to timeout scheduler.

        Returns:
            An observable sequence of buffers.

        See Also:
            - :func:`buffer_with_time <reactivex.operators.buffer_with_time>`
            - :meth:`buffer`
            - :meth:`buffer_with_count`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.buffer_with_time(timespan, timeshift, scheduler)
        )

    def buffer_with_time_or_count(
        self,
        timespan: typing.RelativeTime,
        count: int,
        scheduler: Any = None,
    ) -> Observable[list[_T]]:
        """Buffer elements by time or count.

        Projects each element of an observable sequence into a buffer that is
        completed when either it's full or a given amount of time has elapsed.

        Examples:
            Fluent style:
            >>> result = source.buffer_with_time_or_count(1.0, 5)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.buffer_with_time_or_count(1.0, 5))

        Args:
            timespan: Maximum time length of a buffer.
            count: Maximum element count of a buffer.
            scheduler: Scheduler to run the timer on. If not specified,
                defaults to timeout scheduler.

        Returns:
            An observable sequence of buffers.

        See Also:
            - :func:`buffer_with_time_or_count
              <reactivex.operators.buffer_with_time_or_count>`
            - :meth:`buffer_with_time`
            - :meth:`buffer_with_count`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.buffer_with_time_or_count(timespan, count, scheduler)
        )

    def buffer_when(
        self, closing_mapper: Callable[[], Observable[Any]]
    ) -> Observable[list[_T]]:
        """Buffer elements with dynamic boundaries.

        Projects each element of an observable sequence into zero or more buffers.

        Examples:
            Fluent style:
            >>> result = source.buffer_when(lambda: rx.timer(1.0))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.buffer_when(lambda: rx.timer(1.0)))

        Args:
            closing_mapper: A function invoked to define the closing of each
                produced buffer. A buffer is started when the previous buffer
                is closed. The observable returned by the closing_mapper is
                used to close the buffer when it emits any notification.

        Returns:
            An observable sequence of buffers.

        See Also:
            - :func:`buffer_when <reactivex.operators.buffer_when>`
            - :meth:`buffer`
            - :meth:`buffer_toggle`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.buffer_when(closing_mapper))

    def buffer_toggle(
        self,
        openings: Observable[Any],
        closing_mapper: Callable[[Any], Observable[Any]],
    ) -> Observable[list[_T]]:
        """Buffer elements with opening and closing observables.

        Projects each element of an observable sequence into zero or more buffers.

        Examples:
            Fluent style:
            >>> result = source.buffer_toggle(
            ...     openings=rx.interval(5.0),
            ...     closing_mapper=lambda x: rx.timer(2.0)
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(
            ...     ops.buffer_toggle(
            ...         openings=rx.interval(5.0),
            ...         closing_mapper=lambda x: rx.timer(2.0)
            ...     )
            ... )

        Args:
            openings: Observable sequence whose elements denote the
                opening of buffers.
            closing_mapper: A function invoked to define the closing of
                each produced buffer. Value emitted by openings observable
                is provided as argument. The observable returned by
                closing_mapper is used to close the buffer when it emits
                any notification.

        Returns:
            An observable sequence of buffers.

        See Also:
            - :func:`buffer_toggle <reactivex.operators.buffer_toggle>`
            - :meth:`buffer_when`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.buffer_toggle(openings, closing_mapper))

    def window(self, boundaries: Observable[Any]) -> Observable[Observable[_T]]:
        """Window elements based on boundary observable.

        Projects each element of an observable sequence into zero or more windows
        which are produced based on timing information from another observable
        sequence.

        Examples:
            Fluent style:
            >>> result = source.window(rx.interval(1.0))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.window(rx.interval(1.0)))

        Args:
            boundaries: Observable sequence whose elements denote the creation
                and completion of windows.

        Returns:
            An observable sequence of windows.

        See Also:
            - :func:`window <reactivex.operators.window>`
            - :meth:`window_with_count`
            - :meth:`window_with_time`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.window(boundaries))

    def window_with_count(
        self, count: int, skip: int | None = None
    ) -> Observable[Observable[_T]]:
        """Window elements by count.

        Projects each element of an observable sequence into zero or more windows
        which are produced based on element count information.

        Examples:
            Fluent style:
            >>> result = source.window_with_count(5)
            >>> result = source.window_with_count(5, 3)  # overlapping windows

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.window_with_count(5))

        Args:
            count: Length of each window.
            skip: Number of elements to skip between creation of consecutive
                windows. If not specified, defaults to count.

        Returns:
            An observable sequence of windows.

        See Also:
            - :func:`window_with_count <reactivex.operators.window_with_count>`
            - :meth:`window`
            - :meth:`window_with_time`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.window_with_count(count, skip))

    def window_with_time(
        self,
        timespan: typing.RelativeTime,
        timeshift: typing.RelativeTime | None = None,
        scheduler: Any = None,
    ) -> Observable[Observable[_T]]:
        """Window elements by time.

        Projects each element of an observable sequence into zero or more windows
        which are produced based on timing information.

        Examples:
            Fluent style:
            >>> result = source.window_with_time(1.0)
            >>> result = source.window_with_time(1.0, 0.5)  # overlapping windows

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.window_with_time(1.0))

        Args:
            timespan: Length of each window (in seconds).
            timeshift: Interval between creation of consecutive windows.
                If not specified, defaults to timespan.
            scheduler: Scheduler to run the timer on. If not specified,
                defaults to timeout scheduler.

        Returns:
            An observable sequence of windows.

        See Also:
            - :func:`window_with_time <reactivex.operators.window_with_time>`
            - :meth:`window`
            - :meth:`window_with_count`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.window_with_time(timespan, timeshift, scheduler)
        )

    def window_with_time_or_count(
        self,
        timespan: typing.RelativeTime,
        count: int,
        scheduler: Any = None,
    ) -> Observable[Observable[_T]]:
        """Window elements by time or count.

        Projects each element of an observable sequence into a window that is
        completed when either it's full or a given amount of time has elapsed.

        Examples:
            Fluent style:
            >>> result = source.window_with_time_or_count(1.0, 5)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.window_with_time_or_count(1.0, 5))

        Args:
            timespan: Maximum time length of a window.
            count: Maximum element count of a window.
            scheduler: Scheduler to run the timer on. If not specified,
                defaults to timeout scheduler.

        Returns:
            An observable sequence of windows.

        See Also:
            - :func:`window_with_time_or_count
              <reactivex.operators.window_with_time_or_count>`
            - :meth:`window_with_time`
            - :meth:`window_with_count`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.window_with_time_or_count(timespan, count, scheduler)
        )

    def window_when(
        self, closing_mapper: Callable[[], Observable[Any]]
    ) -> Observable[Observable[_T]]:
        """Window elements with dynamic boundaries.

        Projects each element of an observable sequence into zero or more windows.

        Examples:
            Fluent style:
            >>> result = source.window_when(lambda: rx.timer(1.0))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.window_when(lambda: rx.timer(1.0)))

        Args:
            closing_mapper: A function invoked to define the closing of each
                produced window. A window is started when the previous window
                is closed. The observable returned by the closing_mapper is
                used to close the window when it emits any notification.

        Returns:
            An observable sequence of windows.

        See Also:
            - :func:`window_when <reactivex.operators.window_when>`
            - :meth:`window`
            - :meth:`window_toggle`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.window_when(closing_mapper))

    def window_toggle(
        self,
        openings: Observable[Any],
        closing_mapper: Callable[[Any], Observable[Any]],
    ) -> Observable[Observable[_T]]:
        """Window elements with opening and closing observables.

        Projects each element of an observable sequence into zero or more windows.

        Examples:
            Fluent style:
            >>> result = source.window_toggle(
            ...     openings=rx.interval(5.0),
            ...     closing_mapper=lambda x: rx.timer(2.0)
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(
            ...     ops.window_toggle(
            ...         openings=rx.interval(5.0),
            ...         closing_mapper=lambda x: rx.timer(2.0)
            ...     )
            ... )

        Args:
            openings: Observable sequence whose elements denote the
                opening of windows.
            closing_mapper: A function invoked to define the closing of
                each produced window. Value emitted by openings observable
                is provided as argument. The observable returned by
                closing_mapper is used to close the window when it emits
                any notification.

        Returns:
            An observable sequence of windows.

        See Also:
            - :func:`window_toggle <reactivex.operators.window_toggle>`
            - :meth:`window_when`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.window_toggle(openings, closing_mapper))

    def group_by_until(
        self,
        key_mapper: typing.Mapper[_T, _A],
        element_mapper: typing.Mapper[_T, _B] | None,
        duration_mapper: Callable[[Any], Observable[Any]],
        subject_mapper: Callable[[], Any] | None = None,
    ) -> Observable[Any]:
        """Group elements by key with duration control.

        Groups the elements of an observable sequence according to a specified
        key mapper function and comparer and selects the resulting elements by
        using a specified function. A duration mapper is used to control the
        lifetime of groups.

        Examples:
            Fluent style:
            >>> result = source.group_by_until(
            ...     key_mapper=lambda x: x % 2,
            ...     element_mapper=None,
            ...     duration_mapper=lambda grp: rx.timer(5.0)
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(
            ...     ops.group_by_until(
            ...         key_mapper=lambda x: x % 2,
            ...         element_mapper=None,
            ...         duration_mapper=lambda grp: rx.timer(5.0)
            ...     )
            ... )

        Args:
            key_mapper: A function to extract the key for each element.
            element_mapper: A function to map each source element to an
                element in an observable group.
            duration_mapper: A function to signal the expiration of a group.
            subject_mapper: A function that returns a subject to use for
                each group.

        Returns:
            A sequence of observable groups, each of which corresponds to
            a unique key value, containing all elements that share that
            same key value. When a group is expired, a new group with the
            same key will be created.

        See Also:
            - :func:`group_by_until <reactivex.operators.group_by_until>`
            - :meth:`group_by`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.group_by_until(
                key_mapper, element_mapper, duration_mapper, subject_mapper
            )
        )
