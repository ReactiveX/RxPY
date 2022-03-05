import unittest
from typing import Optional

from reactivex import Observable
from reactivex import operators as ops
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


class TestDistinctUntilChanged(unittest.TestCase):
    def test_default_if_empty_non_empty1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(280, 42),
            on_next(360, 43),
            on_completed(420),
        )

        def create() -> Observable[Optional[int]]:
            return xs.pipe(ops.default_if_empty())

        results = scheduler.start(create)

        assert results.messages == [
            on_next(280, 42),
            on_next(360, 43),
            on_completed(420),
        ]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_default_if_empty_non_empty2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(280, 42), on_next(360, 43), on_completed(420)
        )

        def create():
            return xs.pipe(ops.default_if_empty(-1))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(280, 42),
            on_next(360, 43),
            on_completed(420),
        ]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_default_if_empty_empty1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(420))

        def create():
            return xs.pipe(ops.default_if_empty(None))

        results = scheduler.start(create)

        assert results.messages == [on_next(420, None), on_completed(420)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_default_if_empty_empty2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(420))

        def create():
            return xs.pipe(ops.default_if_empty(-1))

        results = scheduler.start(create)

        assert results.messages == [on_next(420, -1), on_completed(420)]
        assert xs.subscriptions == [subscribe(200, 420)]
