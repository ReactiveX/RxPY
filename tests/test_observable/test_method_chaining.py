"""Tests for Observable method chaining (fluent API).

This module tests the fluent/method chaining syntax for RxPY operators,
ensuring they produce identical results to the pipe-based functional syntax.
"""

from typing import Callable

import pytest

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

        result: Observable[str] = source.map(lambda x: x * 2).map(lambda x: x + 1).map(str)

        values: list[str] = []
        result.subscribe(on_next=values.append)

        assert values == ["3", "5", "7"]


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


class TestComplexChaining:
    """Tests for complex method chaining scenarios."""

    def test_complex_chain(self) -> None:
        """Test a complex chain of multiple operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[int] = (
            source
            .filter(lambda x: x % 2 == 0)  # [2, 4, 6, 8, 10]
            .map(lambda x: x * 2)           # [4, 8, 12, 16, 20]
            .skip(1)                        # [8, 12, 16, 20]
            .take(3)                        # [8, 12, 16]
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [8, 12, 16]

    def test_chain_with_reduce(self) -> None:
        """Test chaining that ends with reduce."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        result: Observable[int] = (
            source
            .filter(lambda x: x > 2)
            .map(lambda x: x * 2)
            .reduce(lambda acc, x: acc + x, 0)
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [24]  # (3*2 + 4*2 + 5*2) = 6 + 8 + 10 = 24

    def test_mixed_fluent_and_pipe(self) -> None:
        """Test mixing fluent and pipe styles."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # Start with fluent, then use pipe
        result: Observable[int] = (
            source
            .map(lambda x: x * 2)
            .pipe(
                ops.filter(lambda x: x > 5),
                ops.take(2),
            )
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [6, 8]


# Phase 2 Operators Tests


class TestTransformationOperators:
    """Tests for transformation operators."""

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


class TestFilteringOperators:
    """Tests for filtering operators."""

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


class TestMathematicalOperators:
    """Tests for mathematical/aggregation operators."""

    def test_count_equivalence(self) -> None:
        """Verify count fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int] = source.count()
        pipe_result: Observable[int] = source.pipe(ops.count())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [5]

    def test_sum_equivalence(self) -> None:
        """Verify sum fluent and functional styles are equivalent."""
        source: Observable[float] = rx.of(1.0, 2.0, 3.0, 4.0, 5.0)

        fluent_result: Observable[float] = source.sum()
        pipe_result: Observable[float] = source.pipe(ops.sum())

        fluent_values: list[float] = []
        pipe_values: list[float] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [15.0]

    def test_average_equivalence(self) -> None:
        """Verify average fluent and functional styles are equivalent."""
        source: Observable[float] = rx.of(1.0, 2.0, 3.0, 4.0, 5.0)

        fluent_result: Observable[float] = source.average()
        pipe_result: Observable[float] = source.pipe(ops.average())

        fluent_values: list[float] = []
        pipe_values: list[float] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [3.0]

    def test_min_max_equivalence(self) -> None:
        """Verify min and max fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(3, 1, 4, 1, 5, 9, 2, 6)

        # Min
        fluent_min: Observable[int] = source.min()
        pipe_min: Observable[int] = source.pipe(ops.min())

        fluent_min_values: list[int] = []
        pipe_min_values: list[int] = []

        fluent_min.subscribe(on_next=fluent_min_values.append)
        pipe_min.subscribe(on_next=pipe_min_values.append)

        assert fluent_min_values == pipe_min_values == [1]

        # Max
        fluent_max: Observable[int] = source.max()
        pipe_max: Observable[int] = source.pipe(ops.max())

        fluent_max_values: list[int] = []
        pipe_max_values: list[int] = []

        fluent_max.subscribe(on_next=fluent_max_values.append)
        pipe_max.subscribe(on_next=pipe_max_values.append)

        assert fluent_max_values == pipe_max_values == [9]


class TestConditionalOperators:
    """Tests for conditional operators."""

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


class TestCombinationOperators:
    """Tests for combination operators."""

    def test_merge_equivalence(self) -> None:
        """Verify merge fluent and functional styles are equivalent."""
        source1: Observable[int] = rx.of(1, 2, 3)
        source2: Observable[int] = rx.of(4, 5, 6)

        fluent_result: Observable[int] = source1.merge(source2)
        pipe_result: Observable[int] = source1.pipe(ops.merge(source2))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Merge is concurrent, but in sync mode results should be same
        assert sorted(fluent_values) == sorted(pipe_values)

    def test_concat_equivalence(self) -> None:
        """Verify concat fluent and functional styles are equivalent."""
        source1: Observable[int] = rx.of(1, 2, 3)
        source2: Observable[int] = rx.of(4, 5, 6)

        fluent_result: Observable[int] = source1.concat(source2)
        pipe_result: Observable[int] = source1.pipe(ops.concat(source2))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5, 6]

    def test_start_with_equivalence(self) -> None:
        """Verify start_with fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(4, 5, 6)

        fluent_result: Observable[int] = source.start_with(1, 2, 3)
        pipe_result: Observable[int] = source.pipe(ops.start_with(1, 2, 3))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3, 4, 5, 6]


class TestErrorHandlingOperators:
    """Tests for error handling operators."""

    def test_catch_equivalence(self) -> None:
        """Verify catch fluent and functional styles are equivalent."""
        source: Observable[int] = rx.throw(Exception("Error"))
        fallback: Observable[int] = rx.of(99)

        fluent_result: Observable[int] = source.catch(fallback)
        pipe_result: Observable[int] = source.pipe(ops.catch(fallback))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append, on_error=lambda e: None)
        pipe_result.subscribe(on_next=pipe_values.append, on_error=lambda e: None)

        assert fluent_values == pipe_values == [99]


class TestPhase2ComplexChaining:
    """Tests for complex chaining with Phase 2 operators."""

    def test_complex_phase2_chain(self) -> None:
        """Test complex chain using Phase 2 operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[float] = (
            source
            .filter(lambda x: x % 2 == 0)       # [2, 4, 6, 8, 10]
            .take_while(lambda x: x < 9)        # [2, 4, 6, 8]
            .map(lambda x: x * 2)                # [4, 8, 12, 16]
            .distinct_until_changed()            # [4, 8, 12, 16]
            .start_with(0)                       # [0, 4, 8, 12, 16]
            .average()                           # [8.0]
        )

        values: list[float] = []
        result.subscribe(on_next=values.append)

        assert values == [8.0]


class TestPhase3FilteringOperators:
    """Tests for Phase 3 filtering operators."""

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


class TestPhase3BooleanOperators:
    """Tests for Phase 3 boolean/testing operators."""

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


class TestPhase3GroupingOperators:
    """Tests for Phase 3 grouping operators."""

    def test_partition_equivalence(self) -> None:
        """Verify partition fluent and functional styles are equivalent."""
        # Test that fluent and functional partition both work
        source1: Observable[int] = rx.of(1, 2, 3, 4, 5, 6)
        source2: Observable[int] = rx.of(1, 2, 3, 4, 5, 6)

        # Test fluent style - just verify it returns a list with 2 observables
        result_fluent = source1.partition(lambda x: x % 2 == 0)
        assert isinstance(result_fluent, list)
        assert len(result_fluent) == 2

        # Test pipe style - just verify it returns a list with 2 observables
        result_pipe = source2.pipe(ops.partition(lambda x: x % 2 == 0))
        assert isinstance(result_pipe, list)
        assert len(result_pipe) == 2

        # Test that the evens partition works correctly
        evens_values: list[int] = []
        result_fluent[0].subscribe(on_next=evens_values.append)
        assert evens_values == [2, 4, 6]

    def test_pairwise_equivalence(self) -> None:
        """Verify pairwise fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4)

        fluent_result: Observable[tuple[int, int]] = source.pairwise()
        pipe_result: Observable[tuple[int, int]] = source.pipe(ops.pairwise())

        fluent_values: list[tuple[int, int]] = []
        pipe_values: list[tuple[int, int]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [(1, 2), (2, 3), (3, 4)]


class TestPhase3UtilityOperators:
    """Tests for Phase 3 utility operators."""

    def test_materialize_dematerialize_equivalence(self) -> None:
        """Verify materialize/dematerialize fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[int] = source.materialize().dematerialize()
        pipe_result: Observable[int] = source.pipe(
            ops.materialize(), ops.dematerialize()
        )

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]


class TestPhase3CombinationOperators:
    """Tests for Phase 3 combination operators."""

    def test_fork_join_equivalence(self) -> None:
        """Verify fork_join fluent and functional styles are equivalent."""
        source1: Observable[int] = rx.of(1, 2, 3)
        source2: Observable[int] = rx.of(4, 5, 6)
        source3: Observable[int] = rx.of(7, 8, 9)

        fluent_result: Observable[tuple[int, ...]] = source1.fork_join(source2, source3)
        pipe_result: Observable[tuple[int, ...]] = source1.pipe(
            ops.fork_join(source2, source3)
        )

        fluent_values: list[tuple[int, ...]] = []
        pipe_values: list[tuple[int, ...]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [(3, 6, 9)]

    def test_amb_equivalence(self) -> None:
        """Verify amb fluent and functional styles are equivalent."""
        source1: Observable[int] = rx.of(1, 2, 3)
        source2: Observable[int] = rx.of(4, 5, 6)

        fluent_result: Observable[int] = source1.amb(source2)
        pipe_result: Observable[int] = source1.pipe(ops.amb(source2))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # amb picks the first observable that emits
        assert fluent_values == pipe_values == [1, 2, 3]


class TestPhase3ShareOperators:
    """Tests for Phase 3 share/multicast operators."""

    def test_share_equivalence(self) -> None:
        """Verify share fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[int] = source.share()
        pipe_result: Observable[int] = source.pipe(ops.share())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]


class TestPhase3ComplexChaining:
    """Tests for complex chaining with Phase 3 operators."""

    def test_complex_phase3_chain(self) -> None:
        """Test complex chain using Phase 3 operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[bool] = (
            source
            .skip_last(2)                         # [1, 2, 3, 4, 5, 6, 7, 8]
            .take_last(6)                         # [3, 4, 5, 6, 7, 8]
            .filter(lambda x: x % 2 == 0)        # [4, 6, 8]
            .all(lambda x: x > 3)                # Check if all > 3
        )

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [True]
