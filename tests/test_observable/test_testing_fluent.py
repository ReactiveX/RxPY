"""Tests for TestingMixin fluent API methods.

This module tests the boolean/testing operators fluent syntax from TestingMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestAllMethodChaining:
    """Tests for all() method."""

    def test_all_equivalence(self) -> None:
        """Verify all fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(2, 4, 6, 8)

        fluent_result: Observable[bool] = source.all(lambda x: x % 2 == 0)
        pipe_result: Observable[bool] = source.pipe(ops.all(lambda x: x % 2 == 0))

        fluent_values: list[bool] = []
        pipe_values: list[bool] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [True]

    def test_all_with_false_result(self) -> None:
        """Test all when condition fails."""
        source: Observable[int] = rx.of(2, 4, 5, 8)

        result: Observable[bool] = source.all(lambda x: x % 2 == 0)

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [False]


class TestSomeMethodChaining:
    """Tests for some() method."""

    def test_some_equivalence(self) -> None:
        """Verify some fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[bool] = source.some(lambda x: x > 3)
        pipe_result: Observable[bool] = source.pipe(ops.some(lambda x: x > 3))

        fluent_values: list[bool] = []
        pipe_values: list[bool] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [True]

    def test_some_with_false_result(self) -> None:
        """Test some when condition never succeeds."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[bool] = source.some(lambda x: x > 10)

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [False]


class TestIsEmptyMethodChaining:
    """Tests for is_empty() method."""

    def test_is_empty_equivalence(self) -> None:
        """Verify is_empty fluent and functional styles are equivalent."""
        source: Observable[int] = rx.empty()

        fluent_result: Observable[bool] = source.is_empty()
        pipe_result: Observable[bool] = source.pipe(ops.is_empty())

        fluent_values: list[bool] = []
        pipe_values: list[bool] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [True]

    def test_is_empty_with_values(self) -> None:
        """Test is_empty with non-empty source."""
        source: Observable[int] = rx.of(1)

        result: Observable[bool] = source.is_empty()

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [False]


class TestContainsMethodChaining:
    """Tests for contains() method."""

    def test_contains_equivalence(self) -> None:
        """Verify contains fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(10, 20, 30, 40)

        fluent_result: Observable[bool] = source.contains(30)
        pipe_result: Observable[bool] = source.pipe(ops.contains(30))

        fluent_values: list[bool] = []
        pipe_values: list[bool] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [True]

    def test_contains_not_found(self) -> None:
        """Test contains when value is not found."""
        source: Observable[int] = rx.of(10, 20, 30)

        result: Observable[bool] = source.contains(99)

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [False]


class TestSequenceEqualMethodChaining:
    """Tests for sequence_equal() method."""

    def test_sequence_equal_equivalence(self) -> None:
        """Verify sequence_equal fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)
        other: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[bool] = source.sequence_equal(other)
        pipe_result: Observable[bool] = source.pipe(ops.sequence_equal(other))

        fluent_values: list[bool] = []
        pipe_values: list[bool] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [True]

    def test_sequence_equal_different(self) -> None:
        """Test sequence_equal with different sequences."""
        source: Observable[int] = rx.of(1, 2, 3)
        other: Observable[int] = rx.of(1, 2, 4)

        result: Observable[bool] = source.sequence_equal(other)

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [False]
