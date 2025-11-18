"""Tests for UtilityMixin fluent API methods.

This module tests the utility operators fluent syntax from UtilityMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

from typing import Any

import pytest

import reactivex as rx
from reactivex import Observable, operators as ops
from reactivex.scheduler import TimeoutScheduler


class TestDoActionMethodChaining:
    """Tests for the do_action() and do() methods."""

    def test_do_action_equivalence(self) -> None:
        """Verify do_action fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)
        side_effects_fluent: list[int] = []
        side_effects_pipe: list[int] = []

        # Fluent style
        fluent_result: Observable[int] = source.do_action(side_effects_fluent.append)

        # Pipe style
        pipe_result: Observable[int] = source.pipe(
            ops.do_action(side_effects_pipe.append)
        )

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]
        assert side_effects_fluent == side_effects_pipe == [1, 2, 3]

    def test_do_alias_equivalence(self) -> None:
        """Verify do (alias) fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)
        side_effects_fluent: list[int] = []
        side_effects_pipe: list[int] = []

        # Fluent style using do (alias)
        fluent_result: Observable[int] = source.do(side_effects_fluent.append)

        # Pipe style
        pipe_result: Observable[int] = source.pipe(
            ops.do_action(side_effects_pipe.append)
        )

        # Both should produce identical results
        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]
        assert side_effects_fluent == side_effects_pipe == [1, 2, 3]

    def test_do_action_with_callbacks(self) -> None:
        """Test do_action with on_error and on_completed callbacks."""
        source: Observable[int] = rx.of(1, 2, 3)
        completed_fluent = False
        completed_pipe = False

        def on_completed_fluent() -> None:
            nonlocal completed_fluent
            completed_fluent = True

        def on_completed_pipe() -> None:
            nonlocal completed_pipe
            completed_pipe = True

        fluent_result = source.do_action(on_completed=on_completed_fluent)
        pipe_result = source.pipe(ops.do_action(on_completed=on_completed_pipe))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]
        assert completed_fluent is True
        assert completed_pipe is True

    def test_do_action_chaining(self) -> None:
        """Test chaining do_action with other operators."""
        source: Observable[int] = rx.of(1, 2, 3)
        side_effects: list[int] = []

        result: Observable[int] = (
            source.do_action(side_effects.append)
            .map(lambda x: x * 2)
            .filter(lambda x: x > 2)
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [4, 6]
        assert side_effects == [1, 2, 3]


class TestTimingOperators:
    """Tests for timing-related operators."""

    def test_timestamp_equivalence(self) -> None:
        """Verify timestamp fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[Any] = source.timestamp()
        pipe_result: Observable[Any] = source.pipe(ops.timestamp())

        fluent_values: list[Any] = []
        pipe_values: list[Any] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Both should have same number of timestamped values
        assert len(fluent_values) == len(pipe_values) == 3
        # Check that values are the same
        for f, p in zip(fluent_values, pipe_values):
            assert f.value == p.value

    def test_time_interval_equivalence(self) -> None:
        """Verify time_interval fluent and functional styles are equivalent."""
        from reactivex.scheduler import ImmediateScheduler

        scheduler = ImmediateScheduler()
        fluent_values: list[Any] = []
        pipe_values: list[Any] = []

        # Use explicit scheduler to avoid timing issues with singleton
        fluent_source: Observable[int] = rx.of(1, 2, 3)
        pipe_source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[Any] = fluent_source.time_interval(scheduler)
        pipe_result: Observable[Any] = pipe_source.pipe(ops.time_interval(scheduler))

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Both should have same number of time interval values
        assert len(fluent_values) == len(pipe_values) == 3
        # Check that values are the same
        for f, p in zip(fluent_values, pipe_values):
            assert f.value == p.value


class TestSchedulingOperators:
    """Tests for scheduling operators."""

    def test_observe_on_method_exists(self) -> None:
        """Verify observe_on method exists and returns observable."""
        source: Observable[int] = rx.of(1, 2, 3)
        scheduler = TimeoutScheduler.singleton()

        # Just verify the method exists and returns an Observable
        result: Observable[int] = source.observe_on(scheduler)
        assert isinstance(result, Observable)

    def test_subscribe_on_method_exists(self) -> None:
        """Verify subscribe_on method exists and returns observable."""
        source: Observable[int] = rx.of(1, 2, 3)
        scheduler = TimeoutScheduler.singleton()

        # Just verify the method exists and returns an Observable
        result: Observable[int] = source.subscribe_on(scheduler)
        assert isinstance(result, Observable)


class TestMaterializeOperators:
    """Tests for materialize and dematerialize operators."""

    def test_materialize_equivalence(self) -> None:
        """Verify materialize fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[Any] = source.materialize()
        pipe_result: Observable[Any] = source.pipe(ops.materialize())

        fluent_values: list[Any] = []
        pipe_values: list[Any] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        # Should have 4 notifications: 3 OnNext + 1 OnCompleted
        assert len(fluent_values) == len(pipe_values) == 4

    def test_dematerialize_equivalence(self) -> None:
        """Verify dematerialize fluent and functional styles are equivalent."""
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

    def test_materialize_dematerialize_chaining(self) -> None:
        """Test materialize/dematerialize in a chain."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[int] = (
            source.map(lambda x: x * 2).materialize().dematerialize()
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [2, 4, 6]


class TestLoopControlOperators:
    """Tests for loop control operators."""

    def test_repeat_equivalence(self) -> None:
        """Verify repeat fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2)

        fluent_result: Observable[int] = source.repeat(3)
        pipe_result: Observable[int] = source.pipe(ops.repeat(3))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 1, 2, 1, 2]

    def test_repeat_with_count(self) -> None:
        """Test repeat with specific count."""
        source: Observable[int] = rx.of(5)

        result: Observable[int] = source.repeat(4)

        values: list[int] = []
        result.subscribe(on_next=values.append)

        assert values == [5, 5, 5, 5]


class TestTerminalOperators:
    """Tests for terminal conversion operators."""

    def test_to_iterable_equivalence(self) -> None:
        """Verify to_iterable fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[list[int]] = source.to_iterable()
        pipe_result: Observable[list[int]] = source.pipe(ops.to_iterable())

        fluent_values: list[list[int]] = []
        pipe_values: list[list[int]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [[1, 2, 3, 4, 5]]

    def test_to_list_equivalence(self) -> None:
        """Verify to_list (alias) fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[list[int]] = source.to_list()
        pipe_result: Observable[list[int]] = source.pipe(ops.to_list())

        fluent_values: list[list[int]] = []
        pipe_values: list[list[int]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [[1, 2, 3, 4, 5]]

    def test_to_list_alias(self) -> None:
        """Verify to_list is an alias for to_iterable."""
        source: Observable[int] = rx.of(1, 2, 3)

        list_result: Observable[list[int]] = source.to_list()
        iterable_result: Observable[list[int]] = source.to_iterable()

        list_values: list[list[int]] = []
        iterable_values: list[list[int]] = []

        list_result.subscribe(on_next=list_values.append)
        iterable_result.subscribe(on_next=iterable_values.append)

        assert list_values == iterable_values == [[1, 2, 3]]

    def test_to_set_equivalence(self) -> None:
        """Verify to_set fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 2, 3, 3, 3)

        fluent_result: Observable[set[int]] = source.to_set()
        pipe_result: Observable[set[int]] = source.pipe(ops.to_set())

        fluent_values: list[set[int]] = []
        pipe_values: list[set[int]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [{1, 2, 3}]

    def test_to_dict_equivalence(self) -> None:
        """Verify to_dict fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[dict[int, int]] = source.to_dict(lambda x: x)
        pipe_result: Observable[dict[int, int]] = source.pipe(ops.to_dict(lambda x: x))

        fluent_values: list[dict[int, int]] = []
        pipe_values: list[dict[int, int]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [{1: 1, 2: 2, 3: 3}]

    def test_to_dict_with_element_mapper(self) -> None:
        """Test to_dict with both key and element mappers."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[dict[int, str]] = source.to_dict(
            lambda x: x, lambda x: f"value_{x}"
        )

        values: list[dict[int, str]] = []
        result.subscribe(on_next=values.append)

        assert values == [{1: "value_1", 2: "value_2", 3: "value_3"}]


class TestIgnoreElementsOperator:
    """Tests for ignore_elements operator."""

    def test_ignore_elements_equivalence(self) -> None:
        """Verify ignore_elements fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)

        fluent_result: Observable[int] = source.ignore_elements()
        pipe_result: Observable[int] = source.pipe(ops.ignore_elements())

        fluent_values: list[int] = []
        pipe_values: list[int] = []
        fluent_completed = False
        pipe_completed = False

        def on_completed_fluent() -> None:
            nonlocal fluent_completed
            fluent_completed = True

        def on_completed_pipe() -> None:
            nonlocal pipe_completed
            pipe_completed = True

        fluent_result.subscribe(
            on_next=fluent_values.append, on_completed=on_completed_fluent
        )
        pipe_result.subscribe(
            on_next=pipe_values.append, on_completed=on_completed_pipe
        )

        # Should ignore all elements but still complete
        assert fluent_values == pipe_values == []
        assert fluent_completed is True
        assert pipe_completed is True


class TestFinallyActionOperator:
    """Tests for finally_action operator."""

    def test_finally_action_equivalence(self) -> None:
        """Verify finally_action fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)
        fluent_called = False
        pipe_called = False

        def fluent_action() -> None:
            nonlocal fluent_called
            fluent_called = True

        def pipe_action() -> None:
            nonlocal pipe_called
            pipe_called = True

        fluent_result: Observable[int] = source.finally_action(fluent_action)
        pipe_result: Observable[int] = source.pipe(ops.finally_action(pipe_action))

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]
        assert fluent_called is True
        assert pipe_called is True

    def test_finally_action_on_error(self) -> None:
        """Test finally_action is called on error."""
        source: Observable[int] = rx.throw(Exception("Test error"))
        action_called = False

        def action() -> None:
            nonlocal action_called
            action_called = True

        result: Observable[int] = source.finally_action(action)

        result.subscribe(on_error=lambda e: None)

        assert action_called is True


class TestAsObservableOperator:
    """Tests for as_observable operator."""

    def test_as_observable_equivalence(self) -> None:
        """Verify as_observable fluent and functional styles are equivalent."""
        source: Observable[int] = rx.of(1, 2, 3)

        fluent_result: Observable[int] = source.as_observable()
        pipe_result: Observable[int] = source.pipe(ops.as_observable())

        fluent_values: list[int] = []
        pipe_values: list[int] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert fluent_values == pipe_values == [1, 2, 3]

    def test_as_observable_hides_identity(self) -> None:
        """Test that as_observable returns a different observable."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[int] = source.as_observable()

        # Should be a different observable instance
        assert result is not source


class TestComplexUtilityChaining:
    """Tests for complex chaining with utility operators."""

    def test_complex_utility_chain(self) -> None:
        """Test complex chain using utility operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        side_effects: list[int] = []

        result: Observable[list[int]] = (
            source.do_action(side_effects.append)
            .filter(lambda x: x > 2)
            .map(lambda x: x * 2)
            .to_list()
        )

        values: list[list[int]] = []
        result.subscribe(on_next=values.append)

        assert values == [[6, 8, 10]]
        assert side_effects == [1, 2, 3, 4, 5]

    def test_mixed_utility_and_transformation(self) -> None:
        """Test mixing utility and transformation operators."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5)
        action_called = False

        def cleanup_action() -> None:
            nonlocal action_called
            action_called = True

        result: Observable[set[int]] = (
            source.map(lambda x: x % 2)
            .do(print)  # Using do alias
            .to_set()
            .finally_action(cleanup_action)
        )

        values: list[set[int]] = []
        result.subscribe(on_next=values.append)

        assert values == [{0, 1}]
        assert action_called is True

    def test_utility_with_repeat(self) -> None:
        """Test utility operators with repeat."""
        source: Observable[int] = rx.of(1, 2)
        side_effects: list[int] = []

        result: Observable[int] = (
            source.do_action(side_effects.append).repeat(2).take(5)
        )

        values: list[int] = []
        result.subscribe(on_next=values.append)

        # repeat(2) gives [1,2,1,2], take(5) cuts to [1,2,1,2]
        assert values == [1, 2, 1, 2]
        # do_action should see all values before take
        assert side_effects == [1, 2, 1, 2]

    def test_materialize_with_terminal_ops(self) -> None:
        """Test materialize with terminal operators."""
        source: Observable[int] = rx.of(1, 2, 3)

        result: Observable[list[Any]] = source.materialize().to_list()

        values: list[list[Any]] = []
        result.subscribe(on_next=values.append)

        # Should have one list containing 4 notifications
        assert len(values) == 1
        assert len(values[0]) == 4  # 3 OnNext + 1 OnCompleted
