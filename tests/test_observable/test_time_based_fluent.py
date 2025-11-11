"""Tests for TimeBasedMixin fluent API methods.

This module tests the time-based operators fluent syntax from TimeBasedMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops
from reactivex.scheduler import ImmediateScheduler


class TestThrottleFirstMethodChaining:
    """Tests for throttle_first() method."""

    def test_throttle_first_equivalence(self) -> None:
        """Verify throttle_first fluent and functional styles are equivalent."""
        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int] = source.throttle_first(100, scheduler)
        pipe_result: Observable[int] = source.pipe(ops.throttle_first(100, scheduler))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # With immediate scheduler, typically gets first value
        assert fluent_values == pipe_values


class TestThrottleWithMapperMethodChaining:
    """Tests for throttle_with_mapper() method."""

    def test_throttle_with_mapper_equivalence(self) -> None:
        """Verify throttle_with_mapper fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        def duration_mapper(x: int) -> Observable[int]:
            return rx.empty()

        fluent_result: Observable[int] = source.throttle_with_mapper(duration_mapper)
        pipe_result: Observable[int] = source.pipe(
            ops.throttle_with_mapper(duration_mapper)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values


class TestThrottleWithTimeoutMethodChaining:
    """Tests for throttle_with_timeout() method."""

    def test_throttle_with_timeout_equivalence(self) -> None:
        """Verify throttle_with_timeout fluent and functional styles are equivalent."""
        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # Use duetime=0 to avoid WouldBlockException with ImmediateScheduler
        fluent_result: Observable[int] = source.throttle_with_timeout(0, scheduler)
        pipe_result: Observable[int] = source.pipe(
            ops.throttle_with_timeout(0, scheduler)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # throttle_with_timeout is an alias for debounce
        assert fluent_values == pipe_values
