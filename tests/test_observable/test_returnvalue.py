import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

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
            return Observable.return_value(42, scheduler)

        results = scheduler.start(factory)
        results.messages.assert_equal(
                            on_next(201, 42),
                            on_completed(201))

    def test_return_disposed(self):
        scheduler = TestScheduler()

        def factory():
            return Observable.return_value(42, scheduler)

        results = scheduler.start(factory, disposed=200)
        results.messages.assert_equal()

    def test_return_disposed_after_next(self):
        scheduler = TestScheduler()
        d = SerialDisposable()
        xs = Observable.return_value(42, scheduler)
        results = scheduler.create_observer()

        def action(scheduler, state):
            def on_next(x):
                d.dispose()
                results.on_next(x)
            def on_error(e):
                results.on_error(e)
            def on_completed():
                results.on_completed()

            d.disposable = xs.subscribe(on_next, on_error, on_completed)
            return d.disposable

        scheduler.schedule_absolute(100, action)
        scheduler.start()
        results.messages.assert_equal(on_next(101, 42))

    def test_return_observer_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.return_value(1, scheduler1)
        xs.subscribe(lambda x: _raise('ex'))

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = Observable.return_value(1, scheduler2)
        ys.subscribe(lambda x: x, lambda ex: ex, lambda: _raise('ex'))

        self.assertRaises(RxException, scheduler2.start)
