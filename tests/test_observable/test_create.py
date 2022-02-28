import unittest

import reactivex
from reactivex.disposable import BooleanDisposable, Disposable
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
def _raise(ex):
    raise RxException(ex)


class TestCreate(unittest.TestCase):
    def test_create_next(self):
        scheduler = TestScheduler()

        def _create():
            def subscribe(o, scheduler=None):
                o.on_next(1)
                o.on_next(2)
                return lambda: None

            return reactivex.create(subscribe)

        results = scheduler.start(_create)
        assert results.messages == [on_next(200, 1), on_next(200, 2)]

    def test_create_completed(self):
        scheduler = TestScheduler()

        def _create():
            def subscribe(o, scheduler=None):
                o.on_completed()
                o.on_next(100)
                o.on_error("ex")
                o.on_completed()
                return lambda: None

            return reactivex.create(subscribe)

        results = scheduler.start(_create)
        assert results.messages == [on_completed(200)]

    def test_create_error(self):
        scheduler = TestScheduler()
        ex = "ex"

        def _create():
            def subscribe(o, scheduler=None):
                o.on_error(ex)
                o.on_next(100)
                o.on_error("foo")
                o.on_completed()
                return lambda: None

            return reactivex.create(subscribe)

        results = scheduler.start(_create)
        assert results.messages == [on_error(200, ex)]

    def test_create_exception(self):
        with self.assertRaises(RxException):
            reactivex.create(lambda o, s: _raise("ex")).subscribe()

    def test_create_dispose(self):
        scheduler = TestScheduler()

        def _create():
            def subscribe(o, scheduler=None):
                is_stopped = [False]
                o.on_next(1)
                o.on_next(2)

                def action1(scheduler, state):
                    if not is_stopped[0]:
                        return o.on_next(3)

                scheduler.schedule_relative(600, action1)

                def action2(scheduler, state):
                    if not is_stopped[0]:
                        return o.on_next(4)

                scheduler.schedule_relative(700, action2)

                def action3(scheduler, state):
                    if not is_stopped[0]:
                        return o.on_next(5)

                scheduler.schedule_relative(900, action3)

                def action4(scheduler, state):
                    if not is_stopped[0]:
                        return o.on_next(6)

                scheduler.schedule_relative(1100, action4)

                def dispose():
                    is_stopped[0] = True

                return dispose

            return reactivex.create(subscribe)

        results = scheduler.start(_create)
        assert results.messages == [
            on_next(200, 1),
            on_next(200, 2),
            on_next(800, 3),
            on_next(900, 4),
        ]

    def test_create_observer_throws(self):
        def subscribe(o, scheduler=None):
            o.on_next(1)
            return lambda: None

        with self.assertRaises(RxException):
            reactivex.create(subscribe).subscribe(lambda x: _raise("ex"))

        def subscribe2(o, scheduler=None):
            o.on_error("exception")
            return lambda: None

        with self.assertRaises(RxException):
            reactivex.create(subscribe2).subscribe(on_error=lambda ex: _raise("ex"))

        def subscribe3(o, scheduler=None):
            o.on_completed()
            return lambda: None

        with self.assertRaises(RxException):
            reactivex.create(subscribe3).subscribe(on_completed=lambda: _raise("ex"))
