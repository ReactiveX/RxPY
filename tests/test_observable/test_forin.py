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


class TestForIn(unittest.TestCase):

    def test_for_basic(self):
        scheduler = TestScheduler()

        def create():
            def selector(x):
                return scheduler.create_cold_observable(send(x * 100 + 10, x * 10 + 1), send(x * 100 + 20, x * 10 + 2), send(x * 100 + 30, x * 10 + 3), close(x * 100 + 40))
            return Observable.for_in([1, 2, 3], selector)

        results = scheduler.start(create=create)
        assert results.messages == [send(310, 11), send(320, 12), send(330, 13), send(550, 21), send(560, 22), send(570, 23), send(890, 31), send(900, 32), send(910, 33), close(920)]

    def test_for_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            def selector(x):
                raise Exception(ex)
            return Observable.for_in([1, 2, 3], selector)
        results = scheduler.start(create=create)
        assert results.messages == [throw(200, ex)]
