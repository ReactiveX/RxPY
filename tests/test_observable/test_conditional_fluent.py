"""Tests for ConditionalMixin fluent API methods.

This module tests the conditional operators fluent syntax from ConditionalMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestDefaultIfEmptyMethodChaining:
    """Tests for default_if_empty() method."""

    def test_default_if_empty_equivalence(self) -> None:
        """Verify default_if_empty fluent and functional styles are equivalent."""
        source: Observable[int] = rx.empty()

        fluent_result: Observable[int] = source.default_if_empty(42)
        pipe_result: Observable[int] = source.pipe(ops.default_if_empty(42))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [42]

    def test_default_if_empty_with_values(self) -> None:
        """Test default_if_empty with non-empty source."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[int] = source.default_if_empty(99)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        # Should return original values, not default
        assert values == [1, 2, 3]


class TestFindMethodChaining:
    """Tests for find() method."""

    def test_find_equivalence(self) -> None:
        """Verify find fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int | None] = source.find(lambda x, i, obs: x > 3)
        pipe_result: Observable[int | None] = source.pipe(
            ops.find(lambda x, i, obs: x > 3)
        )

        fluent_values: list[int | None] = []
        pipe_values: list[int | None] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [4]

    def test_find_not_found(self) -> None:
        """Test find when element is not found."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[int | None] = source.find(lambda x, i, obs: x > 10)

        values: list[int | None] = []
        result.subscribe(on_next=values.append)

        assert values == [None]


class TestFindIndexMethodChaining:
    """Tests for find_index() method."""

    def test_find_index_equivalence(self) -> None:
        """Verify find_index fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int | None] = source.find_index(
            lambda x, i, obs: x > 3
        )
        pipe_result: Observable[int | None] = source.pipe(
            ops.find_index(lambda x, i, obs: x > 3)
        )

        fluent_values: list[int | None] = []
        pipe_values: list[int | None] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [3]

    def test_find_index_not_found(self) -> None:
        """Test find_index when element is not found."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[int | None] = source.find_index(lambda x, i, obs: x > 10)

        values: list[int | None] = []
        result.subscribe(on_next=values.append)

        assert values == [-1]
