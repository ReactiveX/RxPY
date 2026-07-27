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

    def do(
        self,
        on_next: typing.OnNext[_T] | None = None,
        on_error: typing.OnError | None = None,
        on_completed: typing.OnCompleted | None = None,
    ) -> Observable[_T]:
        """Alias for do_action.

        Invoke side effects for each element.

        Examples:
            Fluent style:
            >>> result = source.do(print)

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
            - :meth:`do_action`
        """
        return self.do_action(on_next, on_error, on_completed)

    def do_while(self, condition: typing.Predicate[Observable[_T]]) -> Observable[_T]:
        """Repeat source as long as condition holds.

        Repeats source as long as condition holds emulating a do-while loop.

        Examples:
            Fluent style:
            >>> result = source.do_while(lambda obs: should_continue())

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.do_while(lambda obs: should_continue()))

        Args:
            condition: The condition which determines if the source will be
                repeated.

        Returns:
            An observable sequence which is repeated as long as the condition
            holds.

        See Also:
            - :func:`do_while <reactivex.operators.do_while>`
            - :meth:`while_do`
            - :meth:`repeat`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.do_while(condition))

    def while_do(self, condition: typing.Predicate[Observable[_T]]) -> Observable[_T]:
        """Repeat source as long as condition holds.

        Repeats source as long as condition holds emulating a while loop.

        Examples:
            Fluent style:
            >>> result = source.while_do(lambda obs: should_continue())

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.while_do(lambda obs: should_continue()))

        Args:
            condition: The condition which determines if the source will be
                repeated.

        Returns:
            An observable sequence which is repeated as long as the condition
            holds.

        See Also:
            - :func:`while_do <reactivex.operators.while_do>`
            - :meth:`do_while`
            - :meth:`repeat`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.while_do(condition))

    def finally_action(self, action: typing.Action) -> Observable[_T]:
        """Invoke action after termination.

        Invokes a specified action after the source observable sequence
        terminates gracefully or exceptionally.

        Examples:
            Fluent style:
            >>> result = source.finally_action(lambda: print("Cleanup"))

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.finally_action(lambda: print("Cleanup")))

        Args:
            action: Action to invoke after the source terminates.

        Returns:
            Source sequence with the action-invoking termination behavior
            applied.

        See Also:
            - :func:`finally_action <reactivex.operators.finally_action>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.finally_action(action))

    def ignore_elements(self) -> Observable[_T]:
        """Ignore all elements.

        Ignores all elements in an observable sequence leaving only the
        termination messages.

        Examples:
            Fluent style:
            >>> result = source.ignore_elements()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.ignore_elements())

        Returns:
            An empty observable sequence that signals termination, successful
            or exceptional, of the source sequence.

        See Also:
            - :func:`ignore_elements <reactivex.operators.ignore_elements>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.ignore_elements())

    def repeat(self, repeat_count: int | None = None) -> Observable[_T]:
        """Repeat the sequence.

        Repeats the observable sequence a specified number of times. If the
        repeat count is not specified, the sequence repeats indefinitely.

        Examples:
            Fluent style:
            >>> result = source.repeat(3)
            >>> result = source.repeat()  # infinite

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.repeat(3))

        Args:
            repeat_count: Number of times to repeat the sequence. If not
                specified, repeats indefinitely.

        Returns:
            The observable sequence producing the elements of the given
            sequence repeatedly.

        See Also:
            - :func:`repeat <reactivex.operators.repeat>`
            - :meth:`retry`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.repeat(repeat_count))

    def to_iterable(self) -> Observable[list[_T]]:
        """Convert to iterable.

        Creates an iterable (list) from an observable sequence.

        Examples:
            Fluent style:
            >>> result = source.to_iterable()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.to_iterable())

        Returns:
            An observable sequence containing a single element which is a list
            containing all the elements of the source sequence.

        See Also:
            - :func:`to_iterable <reactivex.operators.to_iterable>`
            - :meth:`to_list`
            - :meth:`to_set`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.to_iterable())

    def to_list(self) -> Observable[list[_T]]:
        """Convert to list.

        Alias for to_iterable. Creates a list from an observable sequence.

        Examples:
            Fluent style:
            >>> result = source.to_list()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.to_list())

        Returns:
            An observable sequence containing a single element which is a list
            containing all the elements of the source sequence.

        See Also:
            - :func:`to_list <reactivex.operators.to_list>`
            - :meth:`to_iterable`
        """
        return self.to_iterable()

    def to_set(self) -> Observable[set[_T]]:
        """Convert to set.

        Converts the observable sequence to a set.

        Examples:
            Fluent style:
            >>> result = source.to_set()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.to_set())

        Returns:
            An observable sequence with a single value of a set containing all
            the elements of the source sequence.

        See Also:
            - :func:`to_set <reactivex.operators.to_set>`
            - :meth:`to_list`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.to_set())

    def to_dict(
        self,
        key_mapper: typing.Mapper[_T, Any],
        element_mapper: typing.Mapper[_T, Any] | None = None,
    ) -> Observable[dict[Any, Any]]:
        """Convert to dictionary.

        Converts the observable sequence to a dictionary (Map).

        Examples:
            Fluent style:
            >>> result = source.to_dict(lambda x: x.id)
            >>> result = source.to_dict(lambda x: x.id, lambda x: x.value)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.to_dict(lambda x: x.id))

        Args:
            key_mapper: A function which produces the key for the dictionary.
            element_mapper: An optional function which produces the element for
                the dictionary. If not present, the value will be the element.

        Returns:
            An observable sequence with a single value of a dictionary
            containing the elements of the source sequence.

        See Also:
            - :func:`to_dict <reactivex.operators.to_dict>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.to_dict(key_mapper, element_mapper))

    def to_future(self, future_ctor: Any = None) -> Any:
        """Convert to future.

        Converts an observable sequence to a Future.

        Examples:
            Fluent style:
            >>> future = source.to_future()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> future = source.pipe(ops.to_future())

        Args:
            future_ctor: A function which returns a future. If not provided,
                defaults to creating an asyncio.Future.

        Returns:
            A future with the last value from the observable sequence.

        See Also:
            - :func:`to_future <reactivex.operators.to_future>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.to_future(future_ctor))

    def to_marbles(
        self,
        timespan: typing.RelativeTime = 0.1,
        scheduler: abc.SchedulerBase | None = None,
    ) -> Observable[str]:
        """Convert to marble diagram.

        Convert an observable sequence into a marble diagram string.

        Examples:
            Fluent style:
            >>> result = source.to_marbles()
            >>> result = source.to_marbles(0.2)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.to_marbles())

        Args:
            timespan: Duration of each time slot in seconds.
            scheduler: Scheduler to use for timing.

        Returns:
            An observable sequence with a single value of a marble diagram
            string.

        See Also:
            - :func:`to_marbles <reactivex.operators.to_marbles>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.to_marbles(timespan, scheduler))

    def delay_with_mapper(
        self,
        subscription_delay: Observable[Any]
        | typing.Mapper[Any, Observable[Any]]
        | None = None,
        delay_duration_mapper: typing.Mapper[_T, Observable[Any]] | None = None,
    ) -> Observable[_T]:
        """Delay with mapper functions.

        Time shifts the observable sequence based on a subscription delay and
        a delay mapper function for each element.

        Examples:
            Fluent style:
            >>> result = source.delay_with_mapper(
            ...     subscription_delay=rx.timer(1.0),
            ...     delay_duration_mapper=lambda x: rx.timer(x * 0.1)
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(
            ...     ops.delay_with_mapper(
            ...         subscription_delay=rx.timer(1.0),
            ...         delay_duration_mapper=lambda x: rx.timer(x * 0.1)
            ...     )
            ... )

        Args:
            subscription_delay: Observable indicating the delay for the
                subscription, or a function that returns such an observable.
            delay_duration_mapper: Selector function to retrieve an observable
                for each element that determines its delay.

        Returns:
            Time-shifted sequence.

        See Also:
            - :func:`delay_with_mapper <reactivex.operators.delay_with_mapper>`
            - :meth:`delay`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.delay_with_mapper(subscription_delay, delay_duration_mapper)
        )

    def timeout_with_mapper(
        self,
        first_timeout: Observable[Any] | None = None,
        timeout_duration_mapper: typing.Mapper[_T, Observable[Any]] | None = None,
        other: Observable[_T] | None = None,
    ) -> Observable[_T]:
        """Timeout with mapper functions.

        Returns the source observable sequence, switching to the other
        observable sequence if a timeout is signaled.

        Examples:
            Fluent style:
            >>> result = source.timeout_with_mapper(
            ...     first_timeout=rx.timer(5.0),
            ...     timeout_duration_mapper=lambda x: rx.timer(1.0)
            ... )

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(
            ...     ops.timeout_with_mapper(
            ...         first_timeout=rx.timer(5.0),
            ...         timeout_duration_mapper=lambda x: rx.timer(1.0)
            ...     )
            ... )

        Args:
            first_timeout: Observable that triggers timeout for the first
                element.
            timeout_duration_mapper: Selector to retrieve an observable that
                triggers timeout for each element.
            other: Sequence to return in case of a timeout.

        Returns:
            The source sequence switching to the other sequence in case of a
            timeout.

        See Also:
            - :func:`timeout_with_mapper <reactivex.operators.timeout_with_mapper>`
            - :meth:`timeout`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(
            ops.timeout_with_mapper(first_timeout, timeout_duration_mapper, other)
        )

    def as_observable(self) -> Observable[_T]:
        """Hide the identity of the observable.

        Hides the identity of an observable sequence.

        Examples:
            Fluent style:
            >>> result = source.as_observable()

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.as_observable())

        Returns:
            An observable sequence that hides the identity of the source
            sequence.

        See Also:
            - :func:`as_observable <reactivex.operators.as_observable>`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.as_observable())
