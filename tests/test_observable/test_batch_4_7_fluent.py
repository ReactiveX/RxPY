"""Tests for Batch 4.7 fluent API methods.

This module tests the remaining specialized operators from Batch 4.7,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops
from reactivex.scheduler import ImmediateScheduler


class TestFirstOrDefaultMethodChaining:
    """Tests for first_or_default() method."""

    def test_first_or_default_with_default(self) -> None:
        """Verify first_or_default returns default when empty."""
        source: Observable[int] = rx.empty()

        fluent_result: Observable[int | None] = source.first_or_default(
            default_value=42
        )
        pipe_result: Observable[int | None] = source.pipe(
            ops.first_or_default(default_value=42)
        )

        fluent_values: list[int | None] = []
        pipe_values: list[int | None] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [42]

    def test_first_or_default_with_predicate(self) -> None:
        """Verify first_or_default with predicate."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int | None] = source.first_or_default(
            lambda x: x > 3, default_value=0
        )
        pipe_result: Observable[int | None] = source.pipe(
            ops.first_or_default(lambda x: x > 3, default_value=0)
        )

        fluent_values: list[int | None] = []
        pipe_values: list[int | None] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [4]


class TestLastOrDefaultMethodChaining:
    """Tests for last_or_default() method."""

    def test_last_or_default_with_default(self) -> None:
        """Verify last_or_default returns default when empty."""
        source: Observable[int] = rx.empty()

        fluent_result: Observable[int | None] = source.last_or_default(
            default_value=42
        )
        pipe_result: Observable[int | None] = source.pipe(
            ops.last_or_default(default_value=42)
        )

        fluent_values: list[int | None] = []
        pipe_values: list[int | None] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [42]

    def test_last_or_default_with_predicate(self) -> None:
        """Verify last_or_default with predicate."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int | None] = source.last_or_default(
            default_value=0, predicate=lambda x: x < 4
        )
        pipe_result: Observable[int | None] = source.pipe(
            ops.last_or_default(default_value=0, predicate=lambda x: x < 4)
        )

        fluent_values: list[int | None] = []
        pipe_values: list[int | None] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [3]


class TestSliceMethodChaining:
    """Tests for slice() method."""

    def test_slice_with_start_stop(self) -> None:
        """Verify slice with start and stop."""
        source: Observable[int] = rx.of(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

        fluent_result: Observable[int] = source.slice(start=2, stop=7)
        pipe_result: Observable[int] = source.pipe(ops.slice(start=2, stop=7))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [2, 3, 4, 5, 6]

    def test_slice_with_step(self) -> None:
        """Verify slice with step."""
        source: Observable[int] = rx.of(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

        fluent_result: Observable[int] = source.slice(start=0, stop=10, step=2)
        pipe_result: Observable[int] = source.pipe(ops.slice(start=0, stop=10, step=2))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [0, 2, 4, 6, 8]


class TestTakeLastBufferMethodChaining:
    """Tests for take_last_buffer() method."""

    def test_take_last_buffer_equivalence(self) -> None:
        """Verify take_last_buffer fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        fluent_result: Observable[list[int]] = source.take_last_buffer(3)
        pipe_result: Observable[list[int]] = source.pipe(ops.take_last_buffer(3))

        fluent_values: list[list[int]] = []
        pipe_values: list[list[int]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [[8, 9, 10]]


class TestSkipWithTimeMethodChaining:
    """Tests for skip_with_time() method."""

    def test_skip_with_time_equivalence(self) -> None:
        """Verify skip_with_time fluent and functional styles are equivalent."""
        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler, duration doesn't matter much for this simple test
        fluent_result: Observable[int] = source.skip_with_time(0, scheduler)
        pipe_result: Observable[int] = source.pipe(ops.skip_with_time(0, scheduler))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5]


class TestTakeWithTimeMethodChaining:
    """Tests for take_with_time() method."""

    def test_take_with_time_equivalence(self) -> None:
        """Verify take_with_time fluent and functional styles are equivalent."""
        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler, use duration=0 to avoid WouldBlockException
        fluent_result: Observable[int] = source.take_with_time(0, scheduler)
        pipe_result: Observable[int] = source.pipe(ops.take_with_time(0, scheduler))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # With duration=0, should take all values emitted immediately
        assert fluent_values == pipe_values


class TestSkipLastWithTimeMethodChaining:
    """Tests for skip_last_with_time() method."""

    def test_skip_last_with_time_equivalence(self) -> None:
        """Verify skip_last_with_time fluent and functional styles are equivalent."""
        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler and duration=0, should take all
        fluent_result: Observable[int] = source.skip_last_with_time(0, scheduler)
        pipe_result: Observable[int] = source.pipe(ops.skip_last_with_time(0, scheduler))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5]


class TestTakeLastWithTimeMethodChaining:
    """Tests for take_last_with_time() method."""

    def test_take_last_with_time_equivalence(self) -> None:
        """Verify take_last_with_time fluent and functional styles are equivalent."""
        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler and large duration, should take all
        fluent_result: Observable[int] = source.take_last_with_time(1000, scheduler)
        pipe_result: Observable[int] = source.pipe(ops.take_last_with_time(1000, scheduler))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5]


class TestSkipUntilWithTimeMethodChaining:
    """Tests for skip_until_with_time() method."""

    def test_skip_until_with_time_equivalence(self) -> None:
        """Verify skip_until_with_time fluent and functional styles are equivalent."""
        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler and start_time in the past, should take all
        fluent_result: Observable[int] = source.skip_until_with_time(0, scheduler)
        pipe_result: Observable[int] = source.pipe(ops.skip_until_with_time(0, scheduler))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5]


class TestTakeUntilWithTimeMethodChaining:
    """Tests for take_until_with_time() method."""

    def test_take_until_with_time_equivalence(self) -> None:
        """Verify take_until_with_time fluent and functional styles are equivalent."""
        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler, use end_time=0 to avoid WouldBlockException
        fluent_result: Observable[int] = source.take_until_with_time(0, scheduler)
        pipe_result: Observable[int] = source.pipe(ops.take_until_with_time(0, scheduler))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # With end_time=0 (past), should take no values
        assert fluent_values == pipe_values


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


class TestPublishValueMethodChaining:
    """Tests for publish_value() method."""

    def test_publish_value_without_mapper(self) -> None:
        """Verify publish_value returns ConnectableObservable."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result = source.publish_value(0)
        pipe_result = source.pipe(ops.publish_value(0))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        # Subscribe before connecting to get the initial value
        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Connect to start emission
        fluent_result.connect()
        pipe_result.connect()

        # Should get initial value (0) plus source values (1, 2, 3)
        assert fluent_values == pipe_values == [0, 1, 2, 3]

    def test_publish_value_with_mapper(self) -> None:
        """Verify publish_value with mapper."""
        source: Observable[int] = rx.of(1, 2, 3)

        def mapper(shared: Observable[int]) -> Observable[int]:
            return shared.take(2)

        fluent_result: Observable[int] = source.publish_value(0, mapper)
        pipe_result: Observable[int] = source.pipe(ops.publish_value(0, mapper))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Should get initial value (0) and first source value (1)
        assert fluent_values == pipe_values == [0, 1]


class TestComplexBatch47Chaining:
    """Tests for complex operation chaining with Batch 4.7 operators."""

    def test_complex_filtering_chain(self) -> None:
        """Test complex chaining with new filtering operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[int] = (
            source.slice(start=1, stop=9)  # [2, 3, 4, 5, 6, 7, 8, 9]
            .filter(lambda x: x % 2 == 0)  # [2, 4, 6, 8]
            .take(3)  # [2, 4, 6]
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [2, 4, 6]

    def test_first_or_default_chain(self) -> None:
        """Test chaining with first_or_default."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # Find first even number, or default to -1
        result: Observable[int | None] = source.first_or_default(
            lambda x: x % 2 == 0, default_value=-1
        )

        values: list[int | None] = []
        result.subscribe(on_next=values.append)

        assert values == [2]

    def test_last_or_default_chain(self) -> None:
        """Test chaining with last_or_default."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # Find last odd number, or default to -1
        result: Observable[int | None] = source.last_or_default(
            default_value=-1, predicate=lambda x: x % 2 == 1
        )

        values: list[int | None] = []
        result.subscribe(on_next=values.append)

        assert values == [5]
