import unittest

from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSum(unittest.TestCase):
    def test_sum_int32_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))

        def create():
            return xs.pipe(ops.sum())

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, 0), on_completed(250)]

    def test_sum_int32_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(150, 1), on_next(210, 2), on_completed(250))

        def create():
            return xs.pipe(ops.sum())
        res = scheduler.start(create=create).messages
        assert res == [on_next(250, 2), on_completed(250)]

    def test_sum_int32_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(150, 1), on_next(210, 2), on_next(220, 3),
                on_next(230, 4), on_completed(250))
        def create():
            return xs.pipe(ops.sum())
        res = scheduler.start(create=create).messages
        assert res == [on_next(250, 2 + 3 + 4), on_completed(250)]

    def test_sum_int32_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

        def create():
            return xs.pipe(ops.sum())
        res = scheduler.start(create=create).messages
        assert res == [on_error(210, ex)]

    def test_sum_int32_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1))
        def create():
            return xs.pipe(ops.sum())
        res = scheduler.start(create=create).messages
        assert res == []

    def test_sum_mapper_regular_int32(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(210, "fo"), on_next(220, "b"), on_next(230, "qux"),
                on_completed(240))

        def create():
            return xs.pipe(ops.sum(lambda x: len(x)))

        res = scheduler.start(create=create)

        assert res.messages == [on_next(240, 6), on_completed(240)]
        assert xs.subscriptions == [subscribe(200, 240)]
