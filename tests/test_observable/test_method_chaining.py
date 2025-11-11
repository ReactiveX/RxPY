"""Tests for Observable method chaining (fluent API).

This module contains tests for complex chaining scenarios and mixed fluent/pipe styles.

The fluent API tests have been reorganized into separate mixin-specific test files:

- test_transformation_fluent.py - TransformationMixin operators (map, reduce, scan, flat_map, etc.)
- test_filtering_fluent.py - FilteringMixin operators (filter, take, skip, first, last, etc.)
- test_mathematical_fluent.py - MathematicalMixin operators (count, sum, average, min, max)
- test_conditional_fluent.py - ConditionalMixin operators (default_if_empty, etc.)
- test_combination_fluent.py - CombinationMixin operators (merge, concat, start_with, etc.)
- test_error_handling_fluent.py - ErrorHandlingMixin operators (catch, retry, etc.)
- test_testing_fluent.py - TestingMixin operators (all, some, is_empty, contains, etc.)
- test_utility_fluent.py - UtilityMixin operators (do_action, materialize, timestamp, etc.)
- test_windowing_fluent.py - WindowingMixin operators (partition, pairwise, group_by, etc.)
- test_multicasting_fluent.py - MulticastingMixin operators (share, publish, etc.)

This file now focuses on:
1. Complex multi-operator chaining scenarios
2. Mixed fluent and pipe style usage
3. Cross-mixin integration tests
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestComplexChaining:
    """Tests for complex method chaining scenarios."""

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

    def test_mixed_fluent_and_pipe(self) -> None:
        """Test mixing fluent and pipe styles."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        # Start with fluent, then use pipe
        result: Observable[int] = source.map(lambda x: x * 2).pipe(
            ops.filter(lambda x: x > 5),
            ops.take(2),
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [6, 8]


class TestCrossMixinChaining:
    """Tests for chaining operators across multiple mixins."""

    def test_transformation_filtering_mathematical(self) -> None:
        """Test chaining transformation, filtering, and mathematical operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[float] = (
            source.filter(lambda x: x % 2 == 0)  # FilteringMixin: [2, 4, 6, 8, 10]
            .take_while(lambda x: x < 9)  # FilteringMixin: [2, 4, 6, 8]
            .map(lambda x: x * 2)  # TransformationMixin: [4, 8, 12, 16]
            .distinct_until_changed()  # FilteringMixin: [4, 8, 12, 16]
            .start_with(0)  # CombinationMixin: [0, 4, 8, 12, 16]
            .average()  # MathematicalMixin: [8.0]
        )

        values: list[float] = []
        result.subscribe(on_next=values.append)

        assert values == [8.0]

    def test_filtering_testing_chain(self) -> None:
        """Test complex chain using filtering and testing operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[bool] = (
            source.skip_last(2)  # FilteringMixin: [1, 2, 3, 4, 5, 6, 7, 8]
            .take_last(6)  # FilteringMixin: [3, 4, 5, 6, 7, 8]
            .filter(lambda x: x % 2 == 0)  # FilteringMixin: [4, 6, 8]
            .all(lambda x: x > 3)  # TestingMixin: Check if all > 3
        )

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [True]

    def test_utility_transformation_terminal(self) -> None:
        """Test utility operators with transformation and terminal operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        side_effects: list[int] = []
        action_called = False

        def cleanup_action() -> None:
            nonlocal action_called
            action_called = True

        result: Observable[list[int]] = (
            source.do_action(side_effects.append)  # UtilityMixin
            .filter(lambda x: x > 2)  # FilteringMixin
            .map(lambda x: x * 2)  # TransformationMixin
            .to_list()  # UtilityMixin
            .finally_action(cleanup_action)  # UtilityMixin
        )

        values: list[list[int]] = []
        result.subscribe(on_next=values.append)

        assert values == [[6, 8, 10]]
        assert side_effects == [1, 2, 3, 4, 5]
        assert action_called is True

    def test_combination_error_handling(self) -> None:
        """Test combination operators with error handling."""
        source: Observable[int] = rx.throw(Exception("Error"))
        fallback: Observable[int] = rx.of(1, 2, 3)

        result: Observable[int] = (
            source.catch(fallback)  # ErrorHandlingMixin
            .start_with(0)  # CombinationMixin
            .take(3)  # FilteringMixin
        )

        values: list[int] = []
        result.subscribe(on_next=values.append, on_error=lambda _: None)

        assert values == [0, 1, 2]

    def test_windowing_transformation_testing(self) -> None:
        """Test windowing with transformation and testing."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6)

        # Test partition followed by operations on one partition
        evens, _odds = source.partition(lambda x: x % 2 == 0)

        result: Observable[bool] = evens.map(
            lambda x: x * 2
        ).all(  # TransformationMixin: [4, 8, 12]
            lambda x: x % 4 == 0
        )  # TestingMixin: Check divisible by 4

        values: list[bool] = []
        result.subscribe(on_next=values.append)

        assert values == [True]


class TestPipeToFluentTransition:
    """Tests for transitioning from pipe to fluent style."""

    def test_pipe_then_fluent(self) -> None:
        """Test using pipe operators then switching to fluent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        result: Observable[int] = (
            source.pipe(
                ops.filter(lambda x: x > 2),
                ops.map(lambda x: x * 2),
            )
            .take(2)
            .skip(1)
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [8]

    def test_fluent_then_pipe_then_fluent(self) -> None:
        """Test alternating between fluent and pipe styles."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8)

        result: Observable[int] = (
            source.filter(lambda x: x > 2)
            .pipe(
                ops.map(lambda x: x * 2),
                ops.take(3),
            )
            .skip(1)
            .pipe(ops.take(1))
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [8]
