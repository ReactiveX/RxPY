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


class TestTimeInterval(unittest.TestCase):
    def test_interval_timespan_basic(self):

        scheduler = TestScheduler()

        def create():
            return Observable.interval(100, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(300, 0), on_next(400, 1), on_next(500, 2), on_next(600, 3), on_next(700, 4), on_next(800, 5), on_next(900, 6))

    def test_interval_timespan_zero(self):
        scheduler = TestScheduler()

        def create():
            return Observable.interval(0, scheduler=scheduler)

        results = scheduler.start(create, disposed=210)
        results.messages.assert_equal(on_next(201, 0), on_next(202, 1), on_next(203, 2), on_next(204, 3), on_next(205, 4), on_next(206, 5), on_next(207, 6), on_next(208, 7), on_next(209, 8))

    def test_interval_timespan_negative(self):
        scheduler = TestScheduler()
        def create():
            return Observable.interval(-1, scheduler=scheduler)

        results = scheduler.start(create, disposed=210)
        results.messages.assert_equal(on_next(201, 0), on_next(202, 1), on_next(203, 2), on_next(204, 3), on_next(205, 4), on_next(206, 5), on_next(207, 6), on_next(208, 7), on_next(209, 8))

    def test_interval_timespan_disposed(self):
        scheduler = TestScheduler()

        def create():
            return Observable.interval(1000, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_interval_timespan_observer_throws(self):
        scheduler = TestScheduler()
        xs = Observable.interval(1, scheduler=scheduler)
        xs.subscribe(lambda x: _raise("ex"))

        with self.assertRaises(RxException):
            scheduler.start()
