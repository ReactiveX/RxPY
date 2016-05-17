import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

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


class TestTimer(unittest.TestCase):
    def test_oneshot_timer_timespan_basic(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(duetime=300, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(500, 0), on_completed(500))

    def test_oneshot_timer_timespan_zero(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(0, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(201, 0), on_completed(201))

    def test_oneshot_timer_timespan_negative(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(-1, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(201, 0), on_completed(201))

    def test_oneshot_timer_timespan_disposed(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(1000, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_oneshot_timer_timespan_observer_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.timer(1, scheduler=scheduler1)
        xs.subscribe(lambda x: _raise("ex"))

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = Observable.timer(1, period=None, scheduler=scheduler2)
        ys.subscribe(on_completed=lambda: _raise("ex"))

        self.assertRaises(RxException, scheduler2.start)

    def test_periodic_timer_basic(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(duetime=300, period=400, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(500, 0), on_next(900, 1))

    def test_periodic_timer_equal_time_and_period(self):
        scheduler = TestScheduler()

        def create():
            return Observable.timer(duetime=300, period=300, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(500, 0), on_next(800, 1))
