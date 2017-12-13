import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestTakeLast(unittest.TestCase):
    def test_take_last_zero_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.take_last(0)

        results = scheduler.start(create)

        assert results.messages == [close(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_take_last_zero_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))

        def create():
            return xs.take_last(0)

        results = scheduler.start(create)

        assert results.messages == [throw(650, ex)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_take_last_zero_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))

        def create():
            return xs.take_last(0)
        results = scheduler.start(create)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_take_last_one_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.take_last(1)

        results = scheduler.start(create)
        assert results.messages == [send(650, 9), close(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_take_last_one_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))

        def create():
            return xs.take_last(1)
        results = scheduler.start(create)

        assert results.messages == [throw(650, ex)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_take_last_One_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))

        def create():
            return xs.take_last(1)

        results = scheduler.start(create)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_take_last_three_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.take_last(3)
        results = scheduler.start(create)

        assert results.messages == [send(650, 7), send(650, 8), send(650, 9), close(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_Take_last_three_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))

        def create():
            return xs.take_last(3)
        results = scheduler.start(create)

        assert results.messages == [throw(650, ex)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_Take_last_three_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))

        def create():
            return xs.take_last(3)
        results = scheduler.start(create)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]
