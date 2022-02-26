import unittest

import rx
from rx.disposable import SerialDisposable
from rx.testing import ReactiveTest, TestScheduler

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


class TestReturnValue(unittest.TestCase):
    def test_return_basic(self):
        scheduler = TestScheduler()

        def factory():
            return rx.return_value(42)

        results = scheduler.start(factory)
        assert results.messages == [on_next(200, 42), on_completed(200)]

    def test_return_disposed(self):
        scheduler = TestScheduler()

        def factory():
            return rx.return_value(42)

        results = scheduler.start(factory, disposed=200)
        assert results.messages == []

    def test_return_disposed_after_next(self):
        scheduler = TestScheduler()
        d = SerialDisposable()
        xs = rx.return_value(42)
        results = scheduler.create_observer()

        def action(scheduler, state):
            def on_next(x):
                d.dispose()
                results.on_next(x)

            def on_error(e):
                results.on_error(e)

            def on_completed():
                results.on_completed()

            d.disposable = xs.subscribe(
                on_next, on_error, on_completed, scheduler=scheduler
            )
            return d.disposable

        scheduler.schedule_absolute(100, action)
        scheduler.start()
        assert results.messages == [on_next(100, 42)]

    def test_return_observer_throws(self):
        scheduler1 = TestScheduler()
        xs = rx.return_value(1)
        xs.subscribe(lambda x: _raise("ex"), scheduler=scheduler1)

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = rx.return_value(1)
        ys.subscribe(
            lambda x: x, lambda ex: ex, lambda: _raise("ex"), scheduler=scheduler2
        )

        self.assertRaises(RxException, scheduler2.start)
