"""Utility operators mixin for Observable."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from reactivex import abc, typing

if TYPE_CHECKING:
    from reactivex.observable import Observable


_T = TypeVar("_T", covariant=True)


class UtilityMixin(Generic[_T]):
    """Mixin providing utility operators for Observable.

    This mixin adds operators that provide utility functionality,
    including side effects, timing, scheduling, and notification handling.
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

    def do_action(
        self,
        on_next: typing.OnNext[_T] | None = None,
        on_error: typing.OnError | None = None,
        on_completed: typing.OnCompleted | None = None,
    ) -> Observable[_T]:
        """Invoke side effects for each element.

        Invokes an action for each element in the observable sequence and invokes
        an action on graceful or exceptional termination.

        Examples:
            Fluent style:
            >>> result = source.do_action(print)
            >>> result = source.do_action(
            ...     on_next=lambda x: print(f"Value: {x}"),
            ...     on_error=lambda e: print(f"Error: {e}"),
            ...     on_completed=lambda: print("Done")
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.do_action(print))

        Args:
            on_next: Action to invoke for each element.
            on_error: Action to invoke upon exceptional termination.
            on_completed: Action to invoke upon graceful termination.

        Returns:
            The source sequence with the side-effecting behavior applied.

        See Also:
            - :func:`do_action <reactivex.operators.do_action>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.do_action(on_next, on_error, on_completed)
        )

    def delay(
        self, duetime: typing.RelativeTime, scheduler: abc.SchedulerBase | None = None
    ) -> Observable[_T]:
        """Delay emissions by a specified time.

        Time shifts the observable sequence by the specified relative time.

        Examples:
            Fluent style:
            >>> result = source.delay(1.0)
            >>> result = source.delay(timedelta(seconds=5))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.delay(1.0))

        Args:
            duetime: Relative time by which to shift the observable sequence.
            scheduler: Scheduler to run the delay timers on.

        Returns:
            Time-shifted sequence.

        See Also:
            - :func:`delay <reactivex.operators.delay>`
            - :meth:`delay_subscription`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.delay(duetime, scheduler))

    def timeout(
        self,
        duetime: typing.AbsoluteOrRelativeTime,
        other: Observable[_T] | None = None,
        scheduler: abc.SchedulerBase | None = None,
    ) -> Observable[_T]:
        """Apply a timeout to the sequence.

        Returns the source observable sequence or the other observable sequence
        if the maximum duration between values elapses.

        Examples:
            Fluent style:
            >>> result = source.timeout(1.0)
            >>> result = source.timeout(5.0, fallback_observable)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.timeout(1.0))

        Args:
            duetime: Maximum duration between values before a timeout occurs.
            other: Sequence to return in case of a timeout.
            scheduler: Scheduler to run the timeout timers on.

        Returns:
            The source sequence switching to the other sequence in case of a timeout.

        See Also:
            - :func:`timeout <reactivex.operators.timeout>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.timeout(duetime, other, scheduler))

    def timestamp(self, scheduler: abc.SchedulerBase | None = None) -> Observable[Any]:
        """Add timestamps to elements.

        Records the timestamp for each value in an observable sequence.

        Examples:
            Fluent style:
            >>> result = source.timestamp()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.timestamp())

        Args:
            scheduler: Scheduler to use for timestamping.

        Returns:
            An observable sequence with timestamp information on elements.

        See Also:
            - :func:`timestamp <reactivex.operators.timestamp>`
            - :meth:`time_interval`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.timestamp(scheduler))

    def observe_on(self, scheduler: abc.SchedulerBase) -> Observable[_T]:
        """Observe on a specific scheduler.

        Wraps the source sequence in order to run its observer callbacks on the
        specified scheduler.

        Examples:
            Fluent style:
            >>> result = source.observe_on(scheduler)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.observe_on(scheduler))

        Args:
            scheduler: Scheduler to notify observers on.

        Returns:
            The source sequence whose observations happen on the specified scheduler.

        See Also:
            - :func:`observe_on <reactivex.operators.observe_on>`
            - :meth:`subscribe_on`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.observe_on(scheduler))

    def subscribe_on(self, scheduler: abc.SchedulerBase) -> Observable[_T]:
        """Subscribe on a specific scheduler.

        Wrap the source sequence in order to run its subscription and unsubscription
        logic on the specified scheduler.

        Examples:
            Fluent style:
            >>> result = source.subscribe_on(scheduler)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.subscribe_on(scheduler))

        Args:
            scheduler: Scheduler to perform subscription and unsubscription actions on.

        Returns:
            The source sequence whose subscriptions and unsubscriptions happen on
            the specified scheduler.

        See Also:
            - :func:`subscribe_on <reactivex.operators.subscribe_on>`
            - :meth:`observe_on`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.subscribe_on(scheduler))

    def materialize(self) -> Observable[Any]:
        """Materialize notifications as explicit values.

        Materializes the implicit notifications of an observable
        sequence as explicit notification values.

        Examples:
            Fluent style:
            >>> result = source.materialize()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.materialize())

        Returns:
            An observable sequence containing the materialized
            notification values from the source sequence.

        See Also:
            - :func:`materialize <reactivex.operators.materialize>`
            - :meth:`dematerialize`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.materialize())

    def dematerialize(self) -> Observable[Any]:
        """Dematerialize explicit notifications.

        Dematerializes the explicit notification values of an
        observable sequence as implicit notifications.

        Examples:
            Fluent style:
            >>> result = source.dematerialize()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.dematerialize())

        Returns:
            An observable sequence exhibiting the behavior
            corresponding to the source sequence's notification values.

        See Also:
            - :func:`dematerialize <reactivex.operators.dematerialize>`
            - :meth:`materialize`
        """
        from reactivex import operators as ops

        # Cast is safe: dematerialize is meant to be called on
        # Observable[Notification[T]]. The fluent API allows chaining
        # this on materialized sequences. The cast preserves type
        # safety for the intended use case where _T is Notification[T].
        from reactivex.notification import Notification

        source: Observable[Notification[Any]] = cast(
            "Observable[Notification[Any]]", self._as_observable()
        )
        return ops.dematerialize()(source)

    def time_interval(
        self, scheduler: abc.SchedulerBase | None = None
    ) -> Observable[Any]:
        """Record time intervals between values.

        Records the time interval between consecutive values in an
        observable sequence.

        Examples:
            Fluent style:
            >>> result = source.time_interval()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.time_interval())

        Args:
            scheduler: Scheduler to use for measuring time intervals.

        Returns:
            An observable sequence with time interval information on values.

        See Also:
            - :func:`time_interval <reactivex.operators.time_interval>`
            - :meth:`timestamp`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.time_interval(scheduler))

    def delay_subscription(
        self,
        duetime: typing.AbsoluteOrRelativeTime,
        scheduler: abc.SchedulerBase | None = None,
    ) -> Observable[_T]:
        """Delay subscription to the source.

        Time shifts the observable sequence by delaying the
        subscription.

        Examples:
            Fluent style:
            >>> result = source.delay_subscription(5.0)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.delay_subscription(5.0))

        Args:
            duetime: Absolute or relative time to delay subscription.
            scheduler: Scheduler to run the subscription delay timer on.

        Returns:
            Time-shifted sequence.

        See Also:
            - :func:`delay_subscription <reactivex.operators.delay_subscription>`
            - :meth:`delay`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.delay_subscription(duetime, scheduler))
