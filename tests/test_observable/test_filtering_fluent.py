"""Tests for FilteringMixin fluent API methods.

This module tests the filtering operators fluent syntax from FilteringMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

from typing import Callable

import reactivex as rx
from reactivex import Observable, operators as ops


class TestFilterMethodChaining:
    """Tests for the filter() method."""

    def test_filter_equivalence(self) -> None:
        """Verify fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6)
        predicate: Callable[[int], bool] = lambda x: x % 2 == 0

        # Fluent style
        fluent_result: Observable[int] = source.filter(predicate)

        # Pipe style
        pipe_result: Observable[int] = source.pipe(ops.filter(predicate))

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [2, 4, 6]

    def test_filter_with_map(self) -> None:
        """Test combining filter with map."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        result: Observable[int] = source.filter(lambda x: x > 2).map(lambda x: x * 10)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [30, 40, 50]


class TestTakeMethodChaining:
    """Tests for the take() method."""

    def test_take_equivalence(self) -> None:
        """Verify fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        # Fluent style
        fluent_result: Observable[int] = source.take(5)

        # Pipe style
        pipe_result: Observable[int] = source.pipe(ops.take(5))

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5]

    def test_take_with_map(self) -> None:
        """Test combining take with map."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        result: Observable[int] = source.take(3).map(lambda x: x * 2)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [2, 4, 6]


class TestSkipMethodChaining:
    """Tests for the skip() method."""

    def test_skip_equivalence(self) -> None:
        """Verify fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        # Fluent style
        fluent_result: Observable[int] = source.skip(5)

        # Pipe style
        pipe_result: Observable[int] = source.pipe(ops.skip(5))

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [6, 7, 8, 9, 10]

    def test_skip_with_take(self) -> None:
        """Test combining skip and take."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[int] = source.skip(3).take(4)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [4, 5, 6, 7]


class TestFirstMethodChaining:
    """Tests for the first() method."""

    def test_first_equivalence(self) -> None:
        """Verify fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # Fluent style
        fluent_result: Observable[int] = source.first()

        # Pipe style
        pipe_result: Observable[int] = source.pipe(ops.first())

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1]

    def test_first_with_predicate(self) -> None:
        """Test first with a predicate."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        predicate: Callable[[int], bool] = lambda x: x > 3

        result: Observable[int] = source.first(predicate)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [4]


class TestLastMethodChaining:
    """Tests for the last() method."""

    def test_last_equivalence(self) -> None:
        """Verify fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # Fluent style
        fluent_result: Observable[int] = source.last()

        # Pipe style
        pipe_result: Observable[int] = source.pipe(ops.last())

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [5]

    def test_last_with_predicate(self) -> None:
        """Test last with a predicate."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        predicate: Callable[[int], bool] = lambda x: x < 4

        result: Observable[int] = source.last(predicate)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [3]


class TestTakeLastMethodChaining:
    """Tests for take_last() method."""

    def test_take_last_equivalence(self) -> None:
        """Verify take_last fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int] = source.take_last(3)
        pipe_result: Observable[int] = source.pipe(ops.take_last(3))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [3, 4, 5]


class TestSkipLastMethodChaining:
    """Tests for skip_last() method."""

    def test_skip_last_equivalence(self) -> None:
        """Verify skip_last fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int] = source.skip_last(2)
        pipe_result: Observable[int] = source.pipe(ops.skip_last(2))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]


class TestElementAtMethodChaining:
    """Tests for element_at() method."""

    def test_element_at_equivalence(self) -> None:
        """Verify element_at fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(10, 20, 30, 40, 50)

        fluent_result: Observable[int] = source.element_at(2)
        pipe_result: Observable[int] = source.pipe(ops.element_at(2))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [30]


class TestElementAtOrDefaultMethodChaining:
    """Tests for element_at_or_default() method."""

    def test_element_at_or_default_equivalence(self) -> None:
        """Verify element_at_or_default fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(10, 20, 30)

        fluent_result: Observable[int] = source.element_at_or_default(5, 99)
        pipe_result: Observable[int] = source.pipe(ops.element_at_or_default(5, 99))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [99]

    def test_element_at_or_default_exists(self) -> None:
        """Test element_at_or_default when element exists."""
        source: Observable[int] = rx.of(10, 20, 30, 40, 50)

        result: Observable[int] = source.element_at_or_default(2, 99)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [30]


class TestSingleMethodChaining:
    """Tests for single() method."""

    def test_single_equivalence(self) -> None:
        """Verify single fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(42)

        fluent_result: Observable[int] = source.single()
        pipe_result: Observable[int] = source.pipe(ops.single())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [42]

    def test_single_with_predicate(self) -> None:
        """Test single with predicate."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        result: Observable[int] = source.single(lambda x: x == 3)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [3]


class TestSingleOrDefaultMethodChaining:
    """Tests for single_or_default() method."""

    def test_single_or_default_equivalence(self) -> None:
        """Verify single_or_default fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(42)

        fluent_result: Observable[int] = source.single_or_default(None, 99)
        pipe_result: Observable[int] = source.pipe(ops.single_or_default(None, 99))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [42]

    def test_single_or_default_empty(self) -> None:
        """Test single_or_default with empty source."""
        source: Observable[int] = rx.empty()

        result: Observable[int] = source.single_or_default(None, 99)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [99]


class TestDistinctOperators:
    """Tests for distinct filtering operators."""

    def test_distinct_equivalence(self) -> None:
        """Verify distinct fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 2, 3, 1, 4)

        fluent_result: Observable[int] = source.distinct()
        pipe_result: Observable[int] = source.pipe(ops.distinct())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4]

    def test_distinct_until_changed_equivalence(self) -> None:
        """Verify distinct_until_changed fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 1, 2, 2, 3, 3, 3, 1)

        fluent_result: Observable[int] = source.distinct_until_changed()
        pipe_result: Observable[int] = source.pipe(ops.distinct_until_changed())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 1]


class TestTakeWhileMethodChaining:
    """Tests for take_while() method."""

    def test_take_while_equivalence(self) -> None:
        """Verify take_while fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 1, 2)

        fluent_result: Observable[int] = source.take_while(lambda x: x < 4)
        pipe_result: Observable[int] = source.pipe(ops.take_while(lambda x: x < 4))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]


class TestSkipWhileMethodChaining:
    """Tests for skip_while() method."""

    def test_skip_while_equivalence(self) -> None:
        """Verify skip_while fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 1, 2)

        fluent_result: Observable[int] = source.skip_while(lambda x: x < 4)
        pipe_result: Observable[int] = source.pipe(ops.skip_while(lambda x: x < 4))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [4, 5, 1, 2]


class TestComplexFilteringChaining:
    """Tests for complex filtering chain scenarios."""

    def test_complex_chain(self) -> None:
        """Test a complex chain of multiple operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[int] = (
            source.filter(lambda x: x % 2 == 0)  # [2, 4, 6, 8, 10]
            .map(lambda x: x * 2)  # [4, 8, 12, 16, 20]
            .skip(1)  # [8, 12, 16, 20]
            .take(3)  # [8, 12, 16]
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [8, 12, 16]

    def test_complex_phase3_chain(self) -> None:
        """Test complex chain using Phase 3 operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[bool] = (
            source.skip_last(2)  # [1, 2, 3, 4, 5, 6, 7, 8]
            .take_last(6)  # [3, 4, 5, 6, 7, 8]
            .filter(lambda x: x % 2 == 0)  # [4, 6, 8]
            .all(lambda x: x > 3)  # Check if all > 3
        )

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [True]


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

        fluent_result: Observable[int | None] = source.last_or_default(default_value=42)
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
        from reactivex.scheduler import ImmediateScheduler

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
        from reactivex.scheduler import ImmediateScheduler

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
        from reactivex.scheduler import ImmediateScheduler

        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler and duration=0, should take all
        fluent_result: Observable[int] = source.skip_last_with_time(0, scheduler)
        pipe_result: Observable[int] = source.pipe(
            ops.skip_last_with_time(0, scheduler)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5]


class TestTakeLastWithTimeMethodChaining:
    """Tests for take_last_with_time() method."""

    def test_take_last_with_time_equivalence(self) -> None:
        """Verify take_last_with_time fluent and functional styles are equivalent."""
        from reactivex.scheduler import ImmediateScheduler

        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler and large duration, should take all
        fluent_result: Observable[int] = source.take_last_with_time(1000, scheduler)
        pipe_result: Observable[int] = source.pipe(
            ops.take_last_with_time(1000, scheduler)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5]


class TestSkipUntilWithTimeMethodChaining:
    """Tests for skip_until_with_time() method."""

    def test_skip_until_with_time_equivalence(self) -> None:
        """Verify skip_until_with_time fluent and functional styles are equivalent."""
        from reactivex.scheduler import ImmediateScheduler

        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler and start_time in the past, should take all
        fluent_result: Observable[int] = source.skip_until_with_time(0, scheduler)
        pipe_result: Observable[int] = source.pipe(
            ops.skip_until_with_time(0, scheduler)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5]


class TestTakeUntilWithTimeMethodChaining:
    """Tests for take_until_with_time() method."""

    def test_take_until_with_time_equivalence(self) -> None:
        """Verify take_until_with_time fluent and functional styles are equivalent."""
        from reactivex.scheduler import ImmediateScheduler

        scheduler = ImmediateScheduler()
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # With immediate scheduler, use end_time=0 to avoid WouldBlockException
        fluent_result: Observable[int] = source.take_until_with_time(0, scheduler)
        pipe_result: Observable[int] = source.pipe(
            ops.take_until_with_time(0, scheduler)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # With end_time=0 (past), should take no values
        assert fluent_values == pipe_values


class TestSingleOrDefaultAsyncMethodChaining:
    """Tests for single_or_default_async() method."""

    def test_single_or_default_async_with_single_element(self) -> None:
        """Verify single_or_default_async with single element."""
        source: Observable[int] = rx.of(42)

        fluent_result: Observable[int] = source.single_or_default_async()
        pipe_result: Observable[int] = source.pipe(ops.single_or_default_async())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [42]

    def test_single_or_default_async_with_empty_and_default(self) -> None:
        """Verify single_or_default_async returns default when empty."""
        source: Observable[int] = rx.empty()

        fluent_result: Observable[int] = source.single_or_default_async(
            has_default=True, default_value=99
        )
        pipe_result: Observable[int] = source.pipe(
            ops.single_or_default_async(has_default=True, default_value=99)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [99]

    def test_single_or_default_async_with_empty_no_default(self) -> None:
        """Verify single_or_default_async errors when empty without default."""
        source: Observable[int] = rx.empty()

        fluent_result: Observable[int] = source.single_or_default_async()
        pipe_result: Observable[int] = source.pipe(ops.single_or_default_async())

        fluent_errors: list[Exception] = []
        pipe_errors: list[Exception] = []

        fluent_result.subscribe(on_error=fluent_errors.append)
        pipe_result.subscribe(on_error=pipe_errors.append)

        assert len(fluent_errors) == len(pipe_errors) == 1
        assert type(fluent_errors[0]).__name__ == type(pipe_errors[0]).__name__

    def test_single_or_default_async_with_multiple_elements(self) -> None:
        """Verify single_or_default_async errors with multiple elements."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[int] = source.single_or_default_async()
        pipe_result: Observable[int] = source.pipe(ops.single_or_default_async())

        fluent_errors: list[Exception] = []
        pipe_errors: list[Exception] = []

        fluent_result.subscribe(on_error=fluent_errors.append)
        pipe_result.subscribe(on_error=pipe_errors.append)

        assert len(fluent_errors) == len(pipe_errors) == 1
        assert "more than one element" in str(fluent_errors[0]).lower()
        assert "more than one element" in str(pipe_errors[0]).lower()

    def test_single_or_default_async_equivalence(self) -> None:
        """Verify single_or_default_async fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(5)

        fluent_result: Observable[int] = source.single_or_default_async(
            has_default=True, default_value=0
        )
        pipe_result: Observable[int] = source.pipe(
            ops.single_or_default_async(has_default=True, default_value=0)
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [5]
