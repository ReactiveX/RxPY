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


class TestMergeAllMethodChaining:
    """Tests for merge_all() method."""

    def test_merge_all_equivalence(self) -> None:
        """Verify merge_all fluent and functional styles are equivalent."""
        inner1: Observable[int] = rx.of(1, 2, 3)
        inner2: Observable[int] = rx.of(4, 5, 6)
        source: Observable[Observable[int]] = rx.of(inner1, inner2)

        fluent_result: Observable[int] = source.merge_all()
        pipe_result: Observable[int] = source.pipe(ops.merge_all())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert sorted(fluent_values) == sorted(pipe_values)


class TestZipWithIterableMethodChaining:
    """Tests for zip_with_iterable() method."""

    def test_zip_with_iterable_equivalence(self) -> None:
        """Verify zip_with_iterable fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)
        iterable: list[str] = ["a", "b", "c"]

        fluent_result: Observable[tuple[int, str]] = source.zip_with_iterable(iterable)
        pipe_result: Observable[tuple[int, str]] = source.pipe(
            ops.zip_with_iterable(iterable)
        )

        fluent_values: list[tuple[int, str]] = []
        pipe_values: list[tuple[int, str]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [(1, "a"), (2, "b"), (3, "c")]


class TestJoinMethodChaining:
    """Tests for join() method."""

    def test_join_equivalence(self) -> None:
        """Verify join fluent and functional styles are equivalent."""
        left: Observable[int] = rx.of(1, 2, 3)
        right: Observable[int] = rx.of(4, 5, 6)

        # Use rx.never() for duration to keep windows open
        duration_mapper = lambda _: rx.never()

        fluent_result: Observable[tuple[int, int]] = left.join(
            right, duration_mapper, duration_mapper
        )
        pipe_result: Observable[tuple[int, int]] = left.pipe(
            ops.join(right, duration_mapper, duration_mapper)
        )

        fluent_values: list[tuple[int, int]] = []
        pipe_values: list[tuple[int, int]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Should get all combinations
        assert len(fluent_values) == len(pipe_values) == 9


class TestGroupJoinMethodChaining:
    """Tests for group_join() method."""

    def test_group_join_equivalence(self) -> None:
        """Verify group_join fluent and functional styles are equivalent."""
        left: Observable[int] = rx.of(1, 2)
        right: Observable[int] = rx.of(4, 5)

        # Use rx.never() for duration to keep windows open
        duration_mapper = lambda _: rx.never()

        fluent_result: Observable[tuple[int, Observable[int]]] = left.group_join(
            right, duration_mapper, duration_mapper
        )
        pipe_result: Observable[tuple[int, Observable[int]]] = left.pipe(
            ops.group_join(right, duration_mapper, duration_mapper)
        )

        fluent_count: list[int] = []
        pipe_count: list[int] = []

        def subscribe_to_group(
            x: tuple[int, Observable[int]], count_list: list[int]
        ) -> None:
            _value, group = x
            group_values: list[int] = []
            group.subscribe(on_next=group_values.append)
            count_list.append(len(group_values))

        fluent_result.subscribe(on_next=lambda x: subscribe_to_group(x, fluent_count))
        pipe_result.subscribe(on_next=lambda x: subscribe_to_group(x, pipe_count))

        assert fluent_count == pipe_count
