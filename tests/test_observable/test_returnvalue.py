import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

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


class TestReturnValue(unittest.TestCase):
    def test_return_basic(self):
        scheduler = TestScheduler()

        def factory():
            return Observable.return_value(42)

        results = scheduler.start(factory)
        results.messages.assert_equal(
                            send(200, 42),
                            close(200))

    def test_return_disposed(self):
        scheduler = TestScheduler()

        def factory():
            return Observable.return_value(42)

        results = scheduler.start(factory, disposed=200)
        results.messages.assert_equal()

    def test_return_disposed_after_next(self):
        scheduler = TestScheduler()
        d = SerialDisposable()
        xs = Observable.return_value(42)
        results = scheduler.create_observer()

        def action(scheduler, state):
            def send(x):
                d.dispose()
                results.send(x)
            def throw(e):
                results.throw(e)
            def close():
                results.close()

            d.disposable = xs.subscribe_callbacks(send, throw, close, scheduler)
            return d.disposable

        scheduler.schedule_absolute(100, action)
        scheduler.start()
        results.messages.assert_equal(send(100, 42))

    def test_return_observer_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.return_value(1)
        xs.subscribe_callbacks(lambda x: _raise('ex'), scheduler=scheduler1)

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = Observable.return_value(1)
        ys.subscribe_callbacks(lambda x: x, lambda ex: ex, lambda: _raise('ex'), scheduler2)

        self.assertRaises(RxException, scheduler2.start)
