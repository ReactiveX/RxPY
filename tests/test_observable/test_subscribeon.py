import unittest

from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSubscribeOn(unittest.TestCase):
    def test_subscribe_on_normal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_completed(250),
        )

        def create():
            return xs.pipe(ops.subscribe_on(scheduler))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_subscribe_on_error(self):
        scheduler = TestScheduler()
        ex = "ex"
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_error(210, ex),
        )

        def create():
            return xs.pipe(ops.subscribe_on(scheduler))

        results = scheduler.start(create)

        assert results.messages == [on_error(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_subscribe_on_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_completed(250),
        )

        def create():
            return xs.pipe(ops.subscribe_on(scheduler))

        results = scheduler.start(create)

        assert results.messages == [on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_subscribe_on_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1))

        def create():
            return xs.pipe(ops.subscribe_on(scheduler))

        results = scheduler.start(create)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]


if __name__ == "__main__":
    unittest.main()
