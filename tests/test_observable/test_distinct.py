import math
import unittest
from typing import NoReturn

import pytest

from reactivex import operators as ops
from reactivex.subject import Subject
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex: Exception) -> NoReturn:
    raise RxException(ex)


class TestDistinctUntilChanged(unittest.TestCase):
    def test_distinct_defaultcomparer_all_distinct(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(280, 4),
            on_next(300, 2),
            on_next(350, 1),
            on_next(380, 3),
            on_next(400, 5),
            on_completed(420),
        )

        def create():
            return xs.pipe(ops.distinct())

        results = scheduler.start(create)

        assert results.messages == [
            on_next(280, 4),
            on_next(300, 2),
            on_next(350, 1),
            on_next(380, 3),
            on_next(400, 5),
            on_completed(420),
        ]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_distinct_default_comparer_some_duplicates(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(280, 4),
            on_next(300, 2),
            on_next(350, 2),
            on_next(380, 3),
            on_next(400, 4),
            on_completed(420),
        )

        def create():
            return xs.pipe(ops.distinct())

        results = scheduler.start(create)

        assert results.messages == [
            on_next(280, 4),
            on_next(300, 2),
            on_next(380, 3),
            on_completed(420),
        ]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_distinct_key_mapper_all_distinct(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(280, 8),
            on_next(300, 4),
            on_next(350, 2),
            on_next(380, 6),
            on_next(400, 10),
            on_completed(420),
        )

        def create():
            def key_mapper(x):
                return x / 2

            return xs.pipe(ops.distinct(key_mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(280, 8),
            on_next(300, 4),
            on_next(350, 2),
            on_next(380, 6),
            on_next(400, 10),
            on_completed(420),
        ]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_distinct_key_mapper_some_duplicates(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(280, 4),
            on_next(300, 2),
            on_next(350, 3),
            on_next(380, 7),
            on_next(400, 5),
            on_completed(420),
        )

        def create():
            def key_mapper(x):
                return math.floor(x / 2.0)

            return xs.pipe(ops.distinct(key_mapper))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(280, 4),
            on_next(300, 2),
            on_next(380, 7),
            on_completed(420),
        ]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_distinct_key_mapper_throws(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(280, 3),
            on_next(300, 2),
            on_next(350, 1),
            on_next(380, 0),
            on_next(400, 4),
            on_completed(420),
        )

        def create():
            def key_mapper(x):
                if not x:
                    raise Exception(ex)
                else:
                    return math.floor(x / 2.0)

            return xs.pipe(ops.distinct(key_mapper))

        results = scheduler.start(create)

        assert results.messages == [on_next(280, 3), on_next(350, 1), on_error(380, ex)]
        assert xs.subscriptions == [subscribe(200, 380)]

    def test_distinct_comparer_throws(self) -> None:
        error = ValueError("comparison failed")
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240)
        )

        def comparer(left: int, right: int) -> bool:
            raise error

        results = scheduler.start(lambda: xs.pipe(ops.distinct(comparer=comparer)))

        assert results.messages == [on_next(210, 1), on_error(220, error)]
        assert results.messages[-1].value.exception is error
        assert xs.subscriptions == [subscribe(200, 220)]

    def test_distinct_default_comparer_throws(self) -> None:
        error = ValueError("equality failed")

        class Value:
            def __eq__(self, other: object) -> bool:
                raise error

        source = Subject[Value]()
        values: list[Value] = []
        errors: list[Exception] = []
        source.pipe(ops.distinct()).subscribe(values.append, errors.append)
        first = Value()
        source.on_next(first)
        source.on_next(Value())
        source.on_next(Value())

        assert len(values) == 1 and values[0] is first
        assert len(errors) == 1 and errors[0] is error
        assert not source.observers

    def test_distinct_comparer_error_does_not_interrupt_other_observers(self) -> None:
        error = ValueError("comparison failed")
        source = Subject[int]()
        distinct_values: list[int] = []
        source_values: list[int] = []
        errors: list[Exception] = []

        def comparer(left: int, right: int) -> bool:
            raise error

        source.pipe(ops.distinct(comparer=comparer)).subscribe(
            distinct_values.append, errors.append
        )
        source.subscribe(source_values.append)
        source.on_next(1)
        source.on_next(2)
        source.on_next(3)
        source.on_completed()

        assert distinct_values == [1]
        assert source_values == [1, 2, 3]
        assert errors == [error]

    def test_distinct_does_not_catch_downstream_error(self) -> None:
        error = ValueError("observer failed")
        source = Subject[int]()
        errors: list[Exception] = []

        def on_value(value: int) -> None:
            raise error

        source.pipe(ops.distinct()).subscribe(on_value, errors.append)

        with pytest.raises(ValueError) as raised:
            source.on_next(1)
        assert raised.value is error
        assert errors == []
