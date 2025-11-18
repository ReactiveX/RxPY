"""Tests for MathematicalMixin fluent API methods.

This module tests the mathematical/aggregation operators fluent syntax from MathematicalMixin,
ensuring they produce identical results to the pipe-based functional syntax.
"""

import reactivex as rx
from reactivex import Observable, operators as ops


class TestCountMethodChaining:
    """Tests for count() method."""

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


class TestSumMethodChaining:
    """Tests for sum() method."""

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


class TestAverageMethodChaining:
    """Tests for average() method."""

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


class TestMinMaxMethodChaining:
    """Tests for min() and max() methods."""

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


class TestMinByMaxByMethodChaining:
    """Tests for min_by() and max_by() methods."""

    def test_min_by_equivalence(self) -> None:
        """Verify min_by fluent and functional styles are equivalent."""
        from typing import NamedTuple

        class Person(NamedTuple):
            name: str
            age: int

        source: Observable[Person] = rx.of(
            Person("Alice", 30),
            Person("Bob", 25),
            Person("Charlie", 25),
            Person("David", 35),
        )

        fluent_result: Observable[list[Person]] = source.min_by(lambda x: x.age)
        pipe_result: Observable[list[Person]] = source.pipe(ops.min_by(lambda x: x.age))

        fluent_values: list[list[Person]] = []
        pipe_values: list[list[Person]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert len(fluent_values) == len(pipe_values) == 1
        assert len(fluent_values[0]) == 2  # Bob and Charlie both age 25
        assert fluent_values[0][0].age == 25
        assert fluent_values[0][1].age == 25

    def test_max_by_equivalence(self) -> None:
        """Verify max_by fluent and functional styles are equivalent."""
        from typing import NamedTuple

        class Person(NamedTuple):
            name: str
            age: int

        source: Observable[Person] = rx.of(
            Person("Alice", 30),
            Person("Bob", 25),
            Person("Charlie", 35),
            Person("David", 35),
        )

        fluent_result: Observable[list[Person]] = source.max_by(lambda x: x.age)
        pipe_result: Observable[list[Person]] = source.pipe(ops.max_by(lambda x: x.age))

        fluent_values: list[list[Person]] = []
        pipe_values: list[list[Person]] = []

        fluent_result.subscribe(on_next=fluent_values.append)
        pipe_result.subscribe(on_next=pipe_values.append)

        assert len(fluent_values) == len(pipe_values) == 1
        assert len(fluent_values[0]) == 2  # Charlie and David both age 35
        assert fluent_values[0][0].age == 35
        assert fluent_values[0][1].age == 35


class TestComplexMathematicalChaining:
    """Tests for complex mathematical operation chaining."""

    def test_filter_with_average(self) -> None:
        """Test filtering followed by average."""
        source: Observable[int] = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        result: Observable[float] = (
            source.filter(lambda x: x % 2 == 0)  # [2, 4, 6, 8, 10]
            .take_while(lambda x: x < 9)  # [2, 4, 6, 8]
            .map(lambda x: x * 2)  # [4, 8, 12, 16]
            .distinct_until_changed()  # [4, 8, 12, 16]
            .start_with(0)  # [0, 4, 8, 12, 16]
            .average()  # [8.0]
        )

        values: list[float] = []
        result.subscribe(on_next=values.append)

        assert values == [8.0]
