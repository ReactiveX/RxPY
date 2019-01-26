import unittest
import pytest

import rx
from rx import operators as ops
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
        xs = scheduler.create_cold_observable(
                on_next(100, 1), on_next(150, 2), on_next(200, 3),
                on_completed(250))
        results = scheduler.start(lambda: xs.pipe(ops.retry()))

        assert results.messages == [
                on_next(300, 1), on_next(350, 2), on_next(400, 3),
                on_completed(450)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_retry_observable_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
                on_next(100, 1), on_next(150, 2), on_next(200, 3))
        results = scheduler.start(lambda: xs.pipe(ops.retry()))

        assert results.messages == [
                on_next(300, 1), on_next(350, 2), on_next(400, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_retry_observable_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
                on_next(100, 1), on_next(150, 2), on_next(200, 3),
                on_error(250, ex))
        results = scheduler.start(lambda: xs.pipe(ops.retry()), disposed=1100)
        assert results.messages == [
                on_next(300, 1), on_next(350, 2), on_next(400, 3),
                on_next(550, 1), on_next(600, 2), on_next(650, 3),
                on_next(800, 1), on_next(850, 2), on_next(900, 3),
                on_next(1050, 1)]
        assert xs.subscriptions == [
                subscribe(200, 450), subscribe(450, 700), subscribe(700, 950),
                subscribe(950, 1100)]

    def test_retry_observable_throws(self):
        scheduler1 = TestScheduler()
        xs = rx.return_value(1).pipe(ops.retry())
        xs.subscribe(lambda x: _raise('ex'), scheduler=scheduler1)

        with pytest.raises(RxException):
            scheduler1.start()

        scheduler2 = TestScheduler()
        ys = rx.throw('ex').pipe(ops.retry())
        d = ys.subscribe(on_error=lambda ex: _raise('ex'), scheduler=scheduler2)

        scheduler2.schedule_absolute(210, lambda sc, st: d.dispose())
        scheduler2.start()

        scheduler3 = TestScheduler()
        zs = rx.return_value(1).pipe(ops.retry())
        zs.subscribe(on_completed=lambda: _raise('ex'), scheduler=scheduler3)

        with pytest.raises(RxException):
            scheduler3.start()

    def test_retry_observable_retry_count_basic(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(
                on_next(5, 1), on_next(10, 2), on_next(15, 3),
                on_error(20, ex))
        results = scheduler.start(lambda: xs.pipe(ops.retry(3)))

        assert results.messages == [
                on_next(205, 1), on_next(210, 2), on_next(215, 3),
                on_next(225, 1), on_next(230, 2), on_next(235, 3),
                on_next(245, 1), on_next(250, 2), on_next(255, 3),
                on_error(260, ex)]
        assert xs.subscriptions == [
                subscribe(200, 220), subscribe(220, 240), subscribe(240, 260)]

    def test_retry_observable_retry_count_dispose(self):
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(
                on_next(5, 1), on_next(10, 2), on_next(15, 3),
                on_error(20, ex))
        results = scheduler.start(lambda: xs.pipe(ops.retry(3)), disposed=231)
        assert results.messages == [
                on_next(205, 1), on_next(210, 2), on_next(215, 3),
                on_next(225, 1), on_next(230, 2)]
        assert xs.subscriptions == [subscribe(200, 220), subscribe(220, 231)]

    def test_retry_observable_retry_count_dispose_ii(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
                on_next(100, 1), on_next(150, 2), on_next(200, 3))
        results = scheduler.start(lambda: xs.pipe(ops.retry(3)))

        assert results.messages == [
                on_next(300, 1), on_next(350, 2), on_next(400, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_retry_observable_retry_count_dispose_iii(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
                on_next(100, 1), on_next(150, 2), on_next(200, 3),
                on_completed(250))
        results = scheduler.start(lambda: xs.pipe(ops.retry(3)))

        assert results.messages == [
                on_next(300, 1), on_next(350, 2), on_next(400, 3),
                on_completed(450)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_retry_observable_retry_count_throws(self):
        scheduler1 = TestScheduler()
        xs = rx.return_value(1).pipe(ops.retry(3))
        xs.subscribe(lambda x: _raise('ex'), scheduler=scheduler1)

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = rx.throw('ex').pipe(ops.retry(100))
        d = ys.subscribe(on_error=lambda ex: _raise('ex'), scheduler=scheduler2)

        def dispose(_, __):
            d.dispose()

        scheduler2.schedule_absolute(0, dispose)
        scheduler2.start()

        scheduler3 = TestScheduler()
        zs = rx.return_value(1).pipe(ops.retry(100))
        zs.subscribe(on_completed=lambda: _raise('ex'), scheduler=scheduler3)

        with pytest.raises(RxException):
            scheduler3.start()

        xss = rx.create(lambda o: _raise('ex')).pipe(ops.retry(100))
        with pytest.raises(Exception):
            xss.subscribe()


if __name__ == '__main__':
    unittest.main()
