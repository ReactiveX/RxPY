import unittest

from rx.core import Observable
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


class TestTimeInterval(unittest.TestCase):
    def test_interval_timespan_basic(self):
        scheduler = TestScheduler()

        def create():
            return Observable.interval(100)

        results = scheduler.start(create)
        assert results.messages == [send(300, 0), send(400, 1), send(500, 2), send(600, 3), send(700, 4), send(800, 5), send(900, 6)]

    # def test_interval_timespan_zero(self):
    #     scheduler = TestScheduler()

    #     def create():
    #         return Observable.interval(0)

    #     results = scheduler.start(create, disposed=210)
    #     assert results.messages == [send(201, 0), send(202, 1), send(203, 2), send(204, 3), send(205, 4), send(206, 5), send(207, 6), send(208, 7), send(209, 8)]

    # def test_interval_timespan_negative(self):
    #     scheduler = TestScheduler()
    #     def create():
    #         return Observable.interval(-1)

    #     results = scheduler.start(create, disposed=210)
    #     assert results.messages == [send(201, 0), send(202, 1), send(203, 2), send(204, 3), send(205, 4), send(206, 5), send(207, 6), send(208, 7), send(209, 8)]

    def test_interval_timespan_disposed(self):
        scheduler = TestScheduler()

        def create():
            return Observable.interval(1000)

        results = scheduler.start(create)
        assert results.messages == []

    def test_interval_timespan_observer_throws(self):
        scheduler = TestScheduler()
        xs = Observable.interval(1)
        xs.subscribe_callbacks(lambda x: _raise("ex"), scheduler=scheduler)

        with self.assertRaises(RxException):
            scheduler.start()
