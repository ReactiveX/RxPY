import unittest
from typing import Any, NoReturn

import reactivex
from reactivex import abc
from reactivex.disposable import Disposable
from reactivex.testing import ReactiveTest, TestScheduler

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
def _raise(ex: str) -> NoReturn:
    raise RxException(ex)


class TestCreate(unittest.TestCase):
    def test_create_next(self):
        scheduler = TestScheduler()

        def _create():
            def subscribe(
                o: abc.ObserverBase[int], scheduler: abc.SchedulerBase | None = None
            ) -> abc.DisposableBase:
                o.on_next(1)
                o.on_next(2)
                return Disposable()

            return reactivex.create(subscribe)

        results = scheduler.start(_create)
        assert results.messages == [on_next(200, 1), on_next(200, 2)]

    def test_create_completed(self):
        scheduler = TestScheduler()

        def _create():
            def subscribe(
                o: abc.ObserverBase[int], scheduler: abc.SchedulerBase | None = None
            ) -> abc.DisposableBase:
                o.on_completed()
                o.on_next(100)
                o.on_error(Exception("ex"))
                o.on_completed()
                return Disposable()

            return reactivex.create(subscribe)

        results = scheduler.start(_create)
        assert results.messages == [on_completed(200)]

    def test_create_error(self):
        scheduler = TestScheduler()
        ex = "ex"

        def _create():
            def subscribe(
                o: abc.ObserverBase[int], scheduler: abc.SchedulerBase | None = None
            ) -> abc.DisposableBase:
                o.on_error(Exception(ex))
                o.on_next(100)
                o.on_error(Exception("foo"))
                o.on_completed()
                return Disposable()

            return reactivex.create(subscribe)

        results = scheduler.start(_create)
        assert results.messages == [on_error(200, ex)]

    def test_create_exception(self):
        def subscribe(
            o: abc.ObserverBase[Any], s: abc.SchedulerBase | None = None
        ) -> abc.DisposableBase:
            _raise("ex")

        with self.assertRaises(RxException):
            reactivex.create(subscribe).subscribe()

    def test_create_dispose(self):
        scheduler = TestScheduler()

        def _create():
            def subscribe(
                o: abc.ObserverBase[int], scheduler: abc.SchedulerBase | None = None
            ) -> abc.DisposableBase:
                assert scheduler is not None
                is_stopped = [False]
                o.on_next(1)
                o.on_next(2)

                def action1(scheduler: abc.SchedulerBase, state: Any) -> None:
                    if not is_stopped[0]:
                        o.on_next(3)

                scheduler.schedule_relative(600, action1)

                def action2(scheduler: abc.SchedulerBase, state: Any) -> None:
                    if not is_stopped[0]:
                        o.on_next(4)

                scheduler.schedule_relative(700, action2)

                def action3(scheduler: abc.SchedulerBase, state: Any) -> None:
                    if not is_stopped[0]:
                        o.on_next(5)

                scheduler.schedule_relative(900, action3)

                def action4(scheduler: abc.SchedulerBase, state: Any) -> None:
                    if not is_stopped[0]:
                        o.on_next(6)

                scheduler.schedule_relative(1100, action4)

                def dispose() -> None:
                    is_stopped[0] = True

                return Disposable(dispose)

            return reactivex.create(subscribe)

        results = scheduler.start(_create)
        assert results.messages == [
            on_next(200, 1),
            on_next(200, 2),
            on_next(800, 3),
            on_next(900, 4),
        ]

    def test_create_observer_throws(self):
        def subscribe(
            o: abc.ObserverBase[int], scheduler: abc.SchedulerBase | None = None
        ) -> abc.DisposableBase:
            o.on_next(1)
            return Disposable()

        with self.assertRaises(RxException):
            reactivex.create(subscribe).subscribe(lambda x: _raise("ex"))

        def subscribe2(
            o: abc.ObserverBase[int], scheduler: abc.SchedulerBase | None = None
        ) -> abc.DisposableBase:
            o.on_error(Exception("exception"))
            return Disposable()

        with self.assertRaises(RxException):
            reactivex.create(subscribe2).subscribe(on_error=lambda ex: _raise("ex"))

        def subscribe3(
            o: abc.ObserverBase[int], scheduler: abc.SchedulerBase | None = None
        ) -> abc.DisposableBase:
            o.on_completed()
            return Disposable()

        with self.assertRaises(RxException):
            reactivex.create(subscribe3).subscribe(on_completed=lambda: _raise("ex"))
