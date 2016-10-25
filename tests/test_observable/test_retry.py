import unittest

from rx.core import Observable
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


class TestRetry(unittest.TestCase):
    def test_retry_observable_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_completed(250))
        results = scheduler.start(lambda: xs.retry())

        results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_completed(450))
        xs.subscriptions.assert_equal(subscribe(200, 450))

    def test_retry_observable_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
        results = scheduler.start(lambda: xs.retry())

        results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
        return xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_retry_observable_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
        results = scheduler.start(lambda: xs.retry(), disposed=1100)
        results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_next(550, 1), on_next(600, 2), on_next(650, 3), on_next(800, 1), on_next(850, 2), on_next(900, 3), on_next(1050, 1))
        return xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1100))

    def test_retry_observable_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.return_value(1, scheduler1).retry()
        xs.subscribe(lambda x: _raise('ex'))

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = Observable.throw_exception('ex', scheduler2).retry()
        d = ys.subscribe(on_error=lambda ex: _raise('ex'))

        scheduler2.schedule_absolute(210, lambda sc, st: d.dispose())
        scheduler2.start()

        scheduler3 = TestScheduler()
        zs = Observable.return_value(1, scheduler3).retry()
        zs.subscribe(on_completed=lambda: _raise('ex'))

        self.assertRaises(RxException, scheduler3.start)

    def test_retry_observable_retry_count_basic(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_error(20, ex))
        results = scheduler.start(lambda: xs.retry(3))

        results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2), on_next(235, 3), on_next(245, 1), on_next(250, 2), on_next(255, 3), on_error(260, ex))
        xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 240), subscribe(240, 260))

    def test_retry_observable_retry_count_dispose(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_error(20, ex))
        results = scheduler.start(lambda: xs.retry(3), disposed=231)
        results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2))
        xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 231))

    def test_retry_observable_retry_count_dispose_ii(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
        results = scheduler.start(lambda: xs.retry(3))

        results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_retry_observable_retry_count_dispose_iii(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_completed(250))
        results = scheduler.start(lambda: xs.retry(3))

        results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_completed(450))
        xs.subscriptions.assert_equal(subscribe(200, 450))

    def test_retry_observable_retry_count_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.return_value(1, scheduler1).retry(3)
        xs.subscribe(lambda x: _raise('ex'))

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = Observable.throw_exception('ex', scheduler2).retry(100)
        d = ys.subscribe(on_error=lambda ex: _raise('ex'))

        scheduler2.schedule_absolute(10, lambda sc, st: d.dispose())

        scheduler2.start()
        scheduler3 = TestScheduler()
        zs = Observable.return_value(1, scheduler3).retry(100)
        zs.subscribe(on_completed=lambda: _raise('ex'))

        self.assertRaises(RxException, scheduler3.start)

        xss = Observable.create(lambda o: _raise('ex')).retry(100)
        self.assertRaises(Exception, xss.subscribe)

if __name__ == '__main__':
    unittest.main()
