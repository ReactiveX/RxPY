"""Time-based operators mixin for Observable."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from reactivex import abc, typing

if TYPE_CHECKING:
    from reactivex.observable import Observable


_T = TypeVar("_T", covariant=True)


class TimeBasedMixin(Generic[_T]):
    """Mixin providing time-based operators for Observable.

    This mixin adds operators that work with time, including sampling and debouncing.
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

    def sample(
        self,
        sampler: typing.RelativeTime | Observable[Any],
        scheduler: abc.SchedulerBase | None = None,
    ) -> Observable[_T]:
        """Sample the sequence at intervals.

        Samples the observable sequence at each interval.

        Examples:
            Fluent style:
            >>> result = source.sample(1.0)
            >>> result = source.sample(trigger_observable)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.sample(1.0))

        Args:
            sampler: Interval or observable that triggers sampling.
            scheduler: Scheduler to use for timing intervals.

        Returns:
            Sampled observable sequence.

        See Also:
            - :func:`sample <reactivex.operators.sample>`
            - :meth:`throttle_first`
            - :meth:`debounce`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.sample(sampler, scheduler))

    def debounce(
        self,
        duetime: typing.RelativeTime,
        scheduler: abc.SchedulerBase | None = None,
    ) -> Observable[_T]:
        """Debounce the sequence.

        Ignores values from an observable sequence which are followed by another
        value before duetime.

        Examples:
            Fluent style:
            >>> result = source.debounce(0.5)

            Equivalent pipe style:
            >>> from reactivex import operators as ops
            >>> result = source.pipe(ops.debounce(0.5))

        Args:
            duetime: Duration of the debounce period for each value.
            scheduler: Scheduler to use for timing debounce.

        Returns:
            The debounced sequence.

        See Also:
            - :func:`debounce <reactivex.operators.debounce>`
            - :meth:`throttle_first`
            - :meth:`sample`
        """
        from reactivex import operators as ops

        return self._as_observable().pipe(ops.debounce(duetime, scheduler))
