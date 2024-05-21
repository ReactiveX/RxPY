import logging
import unittest
from datetime import datetime, timezone

from reactivex.operators import delay
from reactivex.testing import ReactiveTest, TestScheduler

FORMAT = "%(asctime)-15s %(threadName)s %(message)s"
logging.basicConfig(filename="rx.log", format=FORMAT, level=logging.DEBUG)
log = logging.getLogger("Rx")

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


class TestDelay(unittest.TestCase):
    def test_delay_timespan_simple1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_completed(550),
        )

        def create():
            return xs.pipe(delay(100.0))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(350, 2),
            on_next(450, 3),
            on_next(550, 4),
            on_completed(650),
        ]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_datetime_offset_simple1_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_completed(550),
        )

        def create():
            dt = datetime.fromtimestamp(300.0, tz=timezone.utc)
            return xs.pipe(delay(dt))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(350, 2),
            on_next(450, 3),
            on_next(550, 4),
            on_completed(650),
        ]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_timespan_simple2_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_completed(550),
        )

        def create():
            return xs.pipe(delay(50))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(300, 2),
            on_next(400, 3),
            on_next(500, 4),
            on_completed(600),
        ]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_datetime_offset_simple2_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_completed(550),
        )

        def create():
            return xs.pipe(delay(datetime.fromtimestamp(250, tz=timezone.utc)))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(300, 2),
            on_next(400, 3),
            on_next(500, 4),
            on_completed(600),
        ]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_timespan_simple3_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_completed(550),
        )

        def create():
            return xs.pipe(delay(150))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(400, 2),
            on_next(500, 3),
            on_next(600, 4),
            on_completed(700),
        ]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_datetime_offset_simple3_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_completed(550),
        )

        def create():
            return xs.pipe(delay(datetime.fromtimestamp(350, tz=timezone.utc)))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(400, 2),
            on_next(500, 3),
            on_next(600, 4),
            on_completed(700),
        ]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_timespan_error1_impl(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_error(550, ex),
        )

        def create():
            return xs.pipe(delay(50))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(300, 2),
            on_next(400, 3),
            on_next(500, 4),
            on_error(550, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_datetime_offset_error1_impl(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_error(550, ex),
        )

        def create():
            return xs.pipe(delay(datetime.fromtimestamp(250, tz=timezone.utc)))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(300, 2),
            on_next(400, 3),
            on_next(500, 4),
            on_error(550, ex),
        ]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_timespan_error2_impl(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_error(550, ex),
        )

        def create():
            return xs.pipe(delay(150))

        results = scheduler.start(create)

        assert results.messages == [on_next(400, 2), on_next(500, 3), on_error(550, ex)]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_datetime_offset_error2_impl(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(250, 2),
            on_next(350, 3),
            on_next(450, 4),
            on_error(550, ex),
        )

        def create():
            return xs.pipe(delay(datetime.fromtimestamp(350, tz=timezone.utc)))

        results = scheduler.start(create)

        assert results.messages == [on_next(400, 2), on_next(500, 3), on_error(550, ex)]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(550))

        def create():
            return xs.pipe(delay(10))

        results = scheduler.start(create)

        assert results.messages == [on_completed(560)]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(550, ex))

        def create():
            return xs.pipe(delay(10.0))

        results = scheduler.start(create)

        assert results.messages == [on_error(550, ex)]
        assert xs.subscriptions == [subscribe(200, 550)]

    def test_delay_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1))

        def create():
            return xs.pipe(delay(10))

        results = scheduler.start(create)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]
