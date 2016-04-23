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


class TestForIn(unittest.TestCase):

    def test_for_basic(self):
        scheduler = TestScheduler()

        def create():
            def selector(x):
                return scheduler.create_cold_observable(on_next(x * 100 + 10, x * 10 + 1), on_next(x * 100 + 20, x * 10 + 2), on_next(x * 100 + 30, x * 10 + 3), on_completed(x * 100 + 40))
            return Observable.for_in([1, 2, 3], selector)

        results = scheduler.start(create=create)
        results.messages.assert_equal(on_next(310, 11), on_next(320, 12), on_next(330, 13), on_next(550, 21), on_next(560, 22), on_next(570, 23), on_next(890, 31), on_next(900, 32), on_next(910, 33), on_completed(920))

    def test_for_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            def selector(x):
                raise Exception(ex)
            return Observable.for_in([1, 2, 3], selector)
        results = scheduler.start(create=create)
        results.messages.assert_equal(on_error(200, ex))
