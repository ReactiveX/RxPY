import unittest
from datetime import datetime

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


class TestTimeout(unittest.TestCase):
    def test_timeout_in_time(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(230, 3), send(260, 4), send(300, 5), send(350, 6), close(400))

        def create():
            return xs.timeout(500, None)

        results = scheduler.start(create)
        assert results.messages == [send(210, 2), send(230, 3), send(260, 4), send(300, 5), send(350, 6), close(400)]

    def test_timeout_out_of_time(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(230, 3), send(260, 4), send(300, 5), send(350, 6), close(400))

        def create():
            return xs.timeout(205)

        results = scheduler.start(create)
        assert results.messages == [send(210, 2), send(230, 3), send(260, 4), send(300, 5), send(350, 6), close(400)]

    def test_timeout_timeout_occurs_1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 1), send(130, 2), send(310, 3), send(400, 4), close(500))
        ys = scheduler.create_cold_observable(send(50, -1), send(200, -2), send(310, -3), close(320))

        def create():
            return xs.timeout(100, ys)

        results = scheduler.start(create)
        assert results.messages == [send(350, -1), send(500, -2), send(610, -3), close(620)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(300, 620)]

    def test_timeout_timeout_occurs_2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 1), send(130, 2), send(240, 3), send(310, 4), send(430, 5), close(500))
        ys = scheduler.create_cold_observable(send(50, -1), send(200, -2), send(310, -3), close(320))

        def create():
            return xs.timeout(100, ys)

        results = scheduler.start(create)

        assert results.messages == [send(240, 3), send(310, 4), send(460, -1), send(610, -2), send(720, -3), close(730)]
        assert xs.subscriptions == [subscribe(200, 410)]
        assert ys.subscriptions == [subscribe(410, 730)]

    def test_timeout_timeout_occurs_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 1), send(130, 2), send(240, 3), send(310, 4), send(430, 5), close(500))
        ys = scheduler.create_cold_observable()

        def create():
            return xs.timeout(100, ys)

        results = scheduler.start(create)

        assert results.messages == [send(240, 3), send(310, 4)]
        assert xs.subscriptions == [subscribe(200, 410)]
        assert ys.subscriptions == [subscribe(410, 1000)]

    def test_timeout_timeout_occurs_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(close(500))
        ys = scheduler.create_cold_observable(send(100, -1))

        def create():
            return xs.timeout(100, ys)

        results = scheduler.start(create)

        assert results.messages == [send(400, -1)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(300, 1000)]

    def test_timeout_timeout_occurs_error(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(throw(500, 'ex'))
        ys = scheduler.create_cold_observable(send(100, -1))

        def create():
            return xs.timeout(100, ys)

        results = scheduler.start(create)

        assert results.messages == [send(400, -1)]
        assert xs.subscriptions == [subscribe(200, 300)]
        assert ys.subscriptions == [subscribe(300, 1000)]

    def test_timeout_timeout_not_occurs_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(close(250))
        ys = scheduler.create_cold_observable(send(100, -1))

        def create():
            return xs.timeout(100, ys)

        results = scheduler.start(create)

        assert results.messages == [close(250)]
        assert xs.subscriptions == [subscribe(200, 250)]
        assert ys.subscriptions == []

    def test_timeout_timeout_not_occurs_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(throw(250, ex))
        ys = scheduler.create_cold_observable(send(100, -1))

        def create():
            return xs.timeout(100, ys)

        results = scheduler.start(create)

        assert results.messages == [throw(250, ex)]
        assert xs.subscriptions == [subscribe(200, 250)]
        assert ys.subscriptions == []

    def test_timeout_timeout_does_not_occur(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 1), send(130, 2), send(240, 3), send(320, 4), send(410, 5), close(500))
        ys = scheduler.create_cold_observable(send(50, -1), send(200, -2), send(310, -3), close(320))

        def create():
            return xs.timeout(100, ys)

        results = scheduler.start(create)

        assert results.messages == [send(240, 3), send(320, 4), send(410, 5), close(500)]
        assert xs.subscriptions == [subscribe(200, 500)]
        assert ys.subscriptions == []

    def test_timeout_datetime_offset_timeout_occurs(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(410, 1))
        ys = scheduler.create_cold_observable(send(100, -1))

        def create():
            return xs.timeout(datetime.utcfromtimestamp(400/1000.0), ys)

        results = scheduler.start(create)

        assert results.messages == [send(500, -1)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(400, 1000)]

    def test_timeout_datetime_offset_timeout_does_not_occur_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), close(390))
        ys = scheduler.create_cold_observable(send(100, -1))

        def create():
            return xs.timeout(datetime.utcfromtimestamp(400/1000.0), ys)
        results = scheduler.start(create)

        assert results.messages == [send(310, 1), close(390)]
        assert xs.subscriptions == [subscribe(200, 390)]
        assert ys.subscriptions == []

    def test_timeout_datetime_offset_timeout_does_not_occur_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), throw(390, ex))
        ys = scheduler.create_cold_observable(send(100, -1))

        def create():
            return xs.timeout(datetime.utcfromtimestamp(400/1000.0), ys)

        results = scheduler.start(create)

        assert results.messages == [send(310, 1), throw(390, ex)]
        assert xs.subscriptions == [subscribe(200, 390)]
        assert ys.subscriptions == []

    def test_timeout_datetime_offset_timeout_occur_2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable(send(100, -1))

        def create():
            return xs.timeout(datetime.utcfromtimestamp(400/1000.0), ys)

        results = scheduler.start(create)

        assert results.messages == [send(310, 1), send(350, 2), send(500, -1)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(400, 1000)]

    def test_timeout_datetime_offset_timeout_occur_3(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(310, 1), send(350, 2), send(420, 3), close(450))
        ys = scheduler.create_cold_observable()

        def create():
            return xs.timeout(datetime.utcfromtimestamp(400/1000.0), ys)

        results = scheduler.start(create)

        assert results.messages == [send(310, 1), send(350, 2)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert ys.subscriptions == [subscribe(400, 1000)]
