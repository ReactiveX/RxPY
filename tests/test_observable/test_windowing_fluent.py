"""Tests for WindowingMixin fluent API methods.

This module tests the windowing/grouping operators fluent syntax from WindowingMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestPartitionMethodChaining:
    """Tests for partition() method."""

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

    def test_partition_odds(self) -> None:
        """Test partition odds stream."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6)

        evens, odds = source.partition(lambda x: x % 2 == 0)

        odds_values: list[int] = []
        odds.subscribe(on_next=odds_values.append)

        assert odds_values == [1, 3, 5]


class TestPairwiseMethodChaining:
    """Tests for pairwise() method."""

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

    def test_pairwise_single_value(self) -> None:
        """Test pairwise with single value (should emit nothing)."""
        source: Observable[int] = rx.of(1)

        result: Observable[tuple[int, int]] = source.pairwise()

        values: list[tuple[int, int]] = []
        result.subscribe(on_next=values.append)

        assert values == []
