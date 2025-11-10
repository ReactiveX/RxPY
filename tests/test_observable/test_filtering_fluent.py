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
