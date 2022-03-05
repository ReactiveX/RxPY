import unittest
from datetime import datetime

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


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestTakeUntilWithTime(unittest.TestCase):
    def test_takeuntil_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_completed(230)
        )

        def create():
            return xs.pipe(ops.take_until_with_time(datetime.utcfromtimestamp(0)))

        res = scheduler.start(create)

        assert res.messages == [on_completed(200)]
        assert xs.subscriptions == [subscribe(200, 200)]

    def test_takeuntil_late(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1), on_next(220, 2), on_completed(230)
        )

        def create():
            dt = datetime.utcfromtimestamp(250)
            return xs.pipe(ops.take_until_with_time(dt))

        res = scheduler.start(create)

        assert res.messages == [on_next(210, 1), on_next(220, 2), on_completed(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_takeuntil_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_error(210, ex))

        def create():
            dt = datetime.utcfromtimestamp(250)
            return xs.pipe(ops.take_until_with_time(dt))

        res = scheduler.start(create)

        assert res.messages == [on_error(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_takeuntil_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        def create():
            dt = datetime.utcfromtimestamp(250)
            return xs.pipe(ops.take_until_with_time(dt))

        res = scheduler.start(create)

        assert res.messages == [on_completed(250)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_takeuntil_twice1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_completed(270),
        )

        def create():
            dt235 = datetime.utcfromtimestamp(235)
            dt255 = datetime.utcfromtimestamp(255)
            return xs.pipe(
                ops.take_until_with_time(dt255),
                ops.take_until_with_time(dt235),
            )

        res = scheduler.start(create)

        assert res.messages == [
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_completed(235),
        ]
        assert xs.subscriptions == [subscribe(200, 235)]

    def test_takeuntil_twice2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_next(250, 5),
            on_next(260, 6),
            on_completed(270),
        )

        def create():
            dt235 = datetime.utcfromtimestamp(235)
            dt255 = datetime.utcfromtimestamp(255)
            return xs.pipe(
                ops.take_until_with_time(dt235),
                ops.take_until_with_time(dt255),
            )

        res = scheduler.start(create)

        assert res.messages == [
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_completed(235),
        ]
        assert xs.subscriptions == [subscribe(200, 235)]
