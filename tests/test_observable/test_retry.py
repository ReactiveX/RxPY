import unittest
import pytest

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


class TestRetry(unittest.TestCase):
    def test_retry_observable_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3), close(250))
        results = scheduler.start(lambda: xs.retry())

        assert results.messages == [send(300, 1), send(350, 2), send(400, 3), close(450)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_retry_observable_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3))
        results = scheduler.start(lambda: xs.retry())

        assert results.messages == [send(300, 1), send(350, 2), send(400, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_retry_observable_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3), throw(250, ex))
        results = scheduler.start(lambda: xs.retry(), disposed=1100)
        assert results.messages == [send(300, 1), send(350, 2), send(400, 3), send(550, 1), send(600, 2), send(650, 3), send(800, 1), send(850, 2), send(900, 3), send(1050, 1)]
        assert xs.subscriptions == [subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1100)]

    def test_retry_observable_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.return_value(1).retry()
        xs.subscribe_callbacks(lambda x: _raise('ex'), scheduler=scheduler1)

        with pytest.raises(RxException):
            scheduler1.start()

        scheduler2 = TestScheduler()
        ys = Observable.throw_exception('ex').retry()
        d = ys.subscribe_callbacks(throw=lambda ex: _raise('ex'), scheduler=scheduler2)

        scheduler2.schedule_absolute(210, lambda sc, st: d.dispose())
        scheduler2.start()

        scheduler3 = TestScheduler()
        zs = Observable.return_value(1).retry()
        zs.subscribe_callbacks(close=lambda: _raise('ex'), scheduler=scheduler3)

        with pytest.raises(RxException):
            scheduler3.start()

    def test_retry_observable_retry_count_basic(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(send(5, 1), send(10, 2), send(15, 3), throw(20, ex))
        results = scheduler.start(lambda: xs.retry(3))

        assert results.messages == [send(205, 1), send(210, 2), send(215, 3), send(225, 1), send(230, 2), send(235, 3), send(245, 1), send(250, 2), send(255, 3), throw(260, ex)]
        assert xs.subscriptions == [subscribe(200, 220), subscribe(220, 240), subscribe(240, 260)]

    def test_retry_observable_retry_count_dispose(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(send(5, 1), send(10, 2), send(15, 3), throw(20, ex))
        results = scheduler.start(lambda: xs.retry(3), disposed=231)
        assert results.messages == [send(205, 1), send(210, 2), send(215, 3), send(225, 1), send(230, 2)]
        assert xs.subscriptions == [subscribe(200, 220), subscribe(220, 231)]

    def test_retry_observable_retry_count_dispose_ii(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3))
        results = scheduler.start(lambda: xs.retry(3))

        assert results.messages == [send(300, 1), send(350, 2), send(400, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_retry_observable_retry_count_dispose_iii(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3), close(250))
        results = scheduler.start(lambda: xs.retry(3))

        assert results.messages == [send(300, 1), send(350, 2), send(400, 3), close(450)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_retry_observable_retry_count_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.return_value(1).retry(3)
        xs.subscribe_callbacks(lambda x: _raise('ex'), scheduler=scheduler1)

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = Observable.throw_exception('ex').retry(100)
        d = ys.subscribe_callbacks(throw=lambda ex: _raise('ex'), scheduler=scheduler2)

        def dispose(_, __):
            d.dispose()

        scheduler2.schedule_absolute(0, dispose)
        scheduler2.start()

        scheduler3 = TestScheduler()
        zs = Observable.return_value(1).retry(100)
        zs.subscribe_callbacks(close=lambda: _raise('ex'), scheduler=scheduler3)

        with pytest.raises(RxException):
            scheduler3.start()

        xss = Observable.create(lambda o: _raise('ex')).retry(100)
        with pytest.raises(Exception):
            xss.subscribe()

if __name__ == '__main__':
    unittest.main()
