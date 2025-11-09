"""Tests for CombinationMixin fluent API methods.

This module tests the combination operators fluent syntax from CombinationMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestMergeMethodChaining:
    """Tests for merge() method."""

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


class TestConcatMethodChaining:
    """Tests for concat() method."""

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


class TestStartWithMethodChaining:
    """Tests for start_with() method."""

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


class TestForkJoinMethodChaining:
    """Tests for fork_join() method."""

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


class TestAmbMethodChaining:
    """Tests for amb() method."""

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
