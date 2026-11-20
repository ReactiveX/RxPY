import unittest
from typing import Any, NoReturn

import reactivex
from reactivex import abc
from reactivex.disposable import SerialDisposable
from reactivex.testing import ReactiveTest, TestScheduler
from reactivex.testing.mockobserver import MockObserver

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
def _raise(ex: Exception) -> NoReturn:
    raise RxException(ex)


class TestReturnValue(unittest.TestCase):
    def test_return_basic(self):
        scheduler = TestScheduler()

        def factory():
            return reactivex.return_value(42)

        results = scheduler.start(factory)
        assert results.messages == [on_next(200, 42), on_completed(200)]

    def test_return_disposed(self):
        scheduler = TestScheduler()

        def factory():
            return reactivex.return_value(42)

        results = scheduler.start(factory, disposed=200)
        assert results.messages == []

    def test_return_disposed_after_next(self):
        scheduler = TestScheduler()
        d = SerialDisposable()
        xs = reactivex.return_value(42)
        results: MockObserver[int] = scheduler.create_observer()

        def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase:
            def on_next_cb(x: int) -> None:
                d.dispose()
                results.on_next(x)

            def on_error_cb(e: Exception) -> None:
                results.on_error(e)

            def on_completed_cb() -> None:
                results.on_completed()

            d.disposable = xs.subscribe(
                on_next_cb, on_error_cb, on_completed_cb, scheduler=scheduler
            )
            return d.disposable

        scheduler.schedule_absolute(100, action)
        scheduler.start()
        assert results.messages == [on_next(100, 42)]

    def test_return_observer_throws(self):
        scheduler1 = TestScheduler()
        xs = reactivex.return_value(1)
        xs.subscribe(lambda x: _raise(Exception("ex")), scheduler=scheduler1)

        self.assertRaises(RxException, scheduler1.start)

        scheduler2 = TestScheduler()
        ys = reactivex.return_value(1)
        ys.subscribe(
            lambda x: None,
            lambda ex: None,
            lambda: _raise(Exception("ex")),
            scheduler=scheduler2,
        )

        self.assertRaises(RxException, scheduler2.start)
