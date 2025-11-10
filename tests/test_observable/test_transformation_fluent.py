"""Tests for TransformationMixin fluent API methods.

This module tests the transformation operators fluent syntax from TransformationMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

from typing import Callable

import reactivex as rx
from reactivex import Observable, operators as ops


class TestMapMethodChaining:
    """Tests for the map() method."""

    def test_map_equivalence(self) -> None:
        """Verify fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        mapper: Callable[[int], int] = lambda x: x * 2

        # Fluent style
        fluent_result: Observable[int] = source.map(mapper)

        # Pipe style
        pipe_result: Observable[int] = source.pipe(ops.map(mapper))

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [2, 4, 6, 8, 10]

    def test_map_type_transformation(self) -> None:
        """Test that map() correctly transforms types."""
        source: Observable[int] = rx.of(1, 2, 3)

        # Transform int to str
        result: Observable[str] = source.map(str)

        values: list[str] = []
        result.subscribe(on_next=values.append)

        assert values == ["1", "2", "3"]

    def test_map_chaining(self) -> None:
        """Test chaining multiple map operations."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[str] = (
            source.map(lambda x: x * 2).map(lambda x: x + 1).map(str)
        )

        values: list[str] = []
        result.subscribe(on_next=values.append)

        assert values == ["3", "5", "7"]


class TestReduceMethodChaining:
    """Tests for the reduce() method."""

    def test_reduce_equivalence(self) -> None:
        """Verify fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        accumulator: Callable[[int, int], int] = lambda acc, x: acc + x

        # Fluent style
        fluent_result: Observable[int] = source.reduce(accumulator)

        # Pipe style
        pipe_result: Observable[int] = source.pipe(ops.reduce(accumulator))

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [15]

    def test_reduce_with_seed(self) -> None:
        """Test reduce with an initial seed value."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        accumulator: Callable[[int, int], int] = lambda acc, x: acc + x

        result: Observable[int] = source.reduce(accumulator, 10)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [25]

    def test_reduce_type_transformation(self) -> None:
        """Test reduce with type transformation (int to str)."""
        source: Observable[int] = rx.of(1, 2, 3)
        accumulator: Callable[[str, int], str] = lambda acc, x: acc + str(x)

        result: Observable[str] = source.reduce(accumulator, "")

        values: list[str] = []
        result.subscribe(on_next=values.append)

        assert values == ["123"]


class TestScanMethodChaining:
    """Tests for the scan() method."""

    def test_scan_equivalence(self) -> None:
        """Verify fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        accumulator: Callable[[int, int], int] = lambda acc, x: acc + x

        # Fluent style
        fluent_result: Observable[int] = source.scan(accumulator)

        # Pipe style
        pipe_result: Observable[int] = source.pipe(ops.scan(accumulator))

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 3, 6, 10, 15]

    def test_scan_with_seed(self) -> None:
        """Test scan with an initial seed value."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        accumulator: Callable[[int, int], int] = lambda acc, x: acc + x

        result: Observable[int] = source.scan(accumulator, 0)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [1, 3, 6, 10, 15]

    def test_scan_type_transformation(self) -> None:
        """Test scan with type transformation (int to list)."""
        source: Observable[int] = rx.of(1, 2, 3)
        accumulator: Callable[[list[int], int], list[int]] = lambda acc, x: acc + [x]

        result: Observable[list[int]] = source.scan(accumulator, [])

        values: list[list[int]] = []
        result.subscribe(on_next=values.append)

        assert values == [[1], [1, 2], [1, 2, 3]]


class TestFlatMapMethodChaining:
    """Tests for flat map operators."""

    def test_flat_map_equivalence(self) -> None:
        """Verify flat_map fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        # Fluent style
        fluent_result: Observable[int] = source.flat_map(lambda x: rx.of(x, x * 2))

        # Pipe style
        pipe_result: Observable[int] = source.pipe(
            ops.flat_map(lambda x: rx.of(x, x * 2))
        )

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 2, 4, 3, 6]

    def test_concat_map_equivalence(self) -> None:
        """Verify concat_map fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[int] = source.concat_map(lambda x: rx.of(x, x * 2))
        pipe_result: Observable[int] = source.pipe(
            ops.concat_map(lambda x: rx.of(x, x * 2))
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 2, 4, 3, 6]


class TestComplexTransformationChaining:
    """Tests for complex transformation chaining scenarios."""

    def test_chain_with_reduce(self) -> None:
        """Test chaining that ends with reduce."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        result: Observable[int] = (
            source.filter(lambda x: x > 2)
            .map(lambda x: x * 2)
            .reduce(lambda acc, x: acc + x, 0)
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [24]  # (3*2 + 4*2 + 5*2) = 6 + 8 + 10 = 24

    def test_scan_with_map(self) -> None:
        """Test scan combined with map."""
        source: Observable[int] = rx.of(1, 2, 3, 4)

        result: Observable[int] = source.scan(lambda acc, x: acc + x, 0).map(
            lambda x: x * 10
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [10, 30, 60, 100]
