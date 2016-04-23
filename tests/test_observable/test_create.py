import unittest

from rx.core import Observable, Disposable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import BooleanDisposable

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
        def create():
            def subscribe(o):
                o.on_next(1)
                o.on_next(2)
                return lambda: None
            return Observable.create(subscribe)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(200, 1), on_next(200, 2))

    def test_create_completed(self):
        scheduler = TestScheduler()

        def create():
            def subscribe(o):
                o.on_completed()
                o.on_next(100)
                o.on_error('ex')
                o.on_completed()
                return lambda: None
            return Observable.create(subscribe)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(200))

    def test_create_error(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            def subscribe(o):
                o.on_error(ex)
                o.on_next(100)
                o.on_error('foo')
                o.on_completed()
                return lambda: None
            return Observable.create(subscribe)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(200, ex))

    def test_create_exception(self):
        with self.assertRaises(RxException):
            Observable.create(lambda o: _raise('ex')).subscribe()

    def test_create_dispose(self):
        scheduler = TestScheduler()

        def create():
            def subscribe(o):
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
            return Observable.create(subscribe)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(200, 1), on_next(200, 2), on_next(800, 3), on_next(900, 4))

    def test_create_observer_throws(self):
        def subscribe(o):
            o.on_next(1)
            return lambda: None

        with self.assertRaises(RxException):
            Observable.create(subscribe).subscribe(lambda x: _raise('ex'))

        def subscribe2(o):
            o.on_error('exception')
            return lambda: None

        with self.assertRaises(RxException):
            Observable.create(subscribe2).subscribe(on_error=lambda ex: _raise('ex'))

        def subscribe3(o):
            o.on_completed()
            return lambda: None

        with self.assertRaises(RxException):
            Observable.create(subscribe3).subscribe(on_completed=lambda: _raise('ex'))

    def test_create_with_disposable_next(self):
        scheduler = TestScheduler()
        def create():
            def subscribe(o):
                o.on_next(1)
                o.on_next(2)
                return Disposable.empty()
            return Observable.create_with_disposable(subscribe)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(200, 1), on_next(200, 2))

    def test_create_with_disposable_completed(self):
        scheduler = TestScheduler()
        def create():
            def subscribe(o):
                o.on_completed()
                o.on_next(100)
                o.on_error('ex')
                o.on_completed()
                return Disposable.empty()
            return Observable.create_with_disposable(subscribe)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(200))

    def test_create_with_disposable_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        def create():
            def subscribe(o):
                o.on_error(ex)
                o.on_next(100)
                o.on_error('foo')
                o.on_completed()
                return Disposable.empty()

            return Observable.create_with_disposable(subscribe)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(200, ex))

    def test_create_with_disposable_exception(self):
        with self.assertRaises(RxException):
            Observable.create_with_disposable(lambda: o, _raise('ex')).subscribe()

    def test_create_with_disposable_dispose(self):
        scheduler = TestScheduler()

        def create():
            def subscribe(o):
                d = BooleanDisposable()
                o.on_next(1)
                o.on_next(2)

                def action1(scheduler, state):
                    if not d.is_disposed:
                        o.on_next(3)
                scheduler.schedule_relative(600, action1)

                def action2(scheduler, state):
                    if not d.is_disposed:
                        o.on_next(4)
                scheduler.schedule_relative(700, action2)

                def action3(scheduler, state):
                    if not d.is_disposed:
                        o.on_next(5)
                scheduler.schedule_relative(900, action3)

                def action4(scheduler, state):
                    if not d.is_disposed:
                        o.on_next(6)
                scheduler.schedule_relative(1100, action4)

                return d
            return Observable.create_with_disposable(subscribe)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(200, 1), on_next(200, 2), on_next(800, 3), on_next(900, 4))


    def test_create_with_disposable_observer_throws(self):
        def subscribe1(o):
            o.on_next(1)
            return Disposable.empty()

        def on_next(x):
            _raise('ex')

        with self.assertRaises(RxException):
            Observable.create_with_disposable(subscribe1).subscribe(on_next)

        def subscribe2(o):
            o.on_error('exception')
            return Disposable.empty()

        with self.assertRaises(RxException):
            Observable.create_with_disposable(subscribe2).subscribe(on_error=lambda ex: _raise('ex'))

        def subscribe3(o):
            o.on_completed()
            return Disposable.empty()

        with self.assertRaises(RxException):
            Observable.create_with_disposable(subscribe3).subscribe(on_completed=_raise('ex'))

