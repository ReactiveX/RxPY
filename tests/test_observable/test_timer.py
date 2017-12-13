import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestTimer(unittest.TestCase):
    def test_oneshot_timer_timespan_basic(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(duetime=300)

        results = scheduler.start(create)
        assert results.messages == [send(500, 0), close(500)]

    def test_oneshot_timer_timespan_zero(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(0)

        results = scheduler.start(create)
        assert results.messages == [send(200, 0), close(200)]

    def test_oneshot_timer_timespan_negative(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(-1)

        results = scheduler.start(create)
        assert results.messages == [send(200, 0), close(200)]

    def test_oneshot_timer_timespan_disposed(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(1000)

        results = scheduler.start(create)
        assert results.messages == []

    def test_oneshot_timer_timespan_observer_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.timer(11)
        xs.subscribe_callbacks(lambda x: _raise("ex"), scheduler=scheduler1)

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = Observable.timer(1, period=None)
        ys.subscribe_callbacks(close=lambda: _raise("ex"), scheduler=scheduler2)

        self.assertRaises(RxException, scheduler2.start)

    def test_periodic_timer_basic(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(duetime=300, period=400)

        results = scheduler.start(create)
        assert results.messages == [send(500, 0), send(900, 1)]

    def test_periodic_timer_equal_time_and_period(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(duetime=300, period=300)

        results = scheduler.start(create)
        assert results.messages == [send(500, 0), send(800, 1)]
