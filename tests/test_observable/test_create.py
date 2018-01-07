import unittest

from rx.core import Observable, Disposable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import BooleanDisposable

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


class TestCreate(unittest.TestCase):

    def test_create_next(self):
        scheduler = TestScheduler()
        def create():
            def subscribe(o, observer=None):
                o.send(1)
                o.send(2)
                return lambda: None
            return Observable.create(subscribe)

        results = scheduler.start(create)
        assert results.messages == [send(200, 1), send(200, 2)]

    def test_create_completed(self):
        scheduler = TestScheduler()

        def create():
            def subscribe(o, observer=None):
                o.close()
                o.send(100)
                o.throw('ex')
                o.close()
                return lambda: None
            return Observable.create(subscribe)

        results = scheduler.start(create)
        assert results.messages == [close(200)]

    def test_create_error(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            def subscribe(o, observer=None):
                o.throw(ex)
                o.send(100)
                o.throw('foo')
                o.close()
                return lambda: None
            return Observable.create(subscribe)

        results = scheduler.start(create)
        assert results.messages == [throw(200, ex)]

    def test_create_exception(self):
        with self.assertRaises(RxException):
            Observable.create(lambda o: _raise('ex')).subscribe()

    def test_create_dispose(self):
        scheduler = TestScheduler()

        def create():
            def subscribe(o, observer=None):
                is_stopped = [False]
                o.send(1)
                o.send(2)

                def action1(scheduler, state):
                    if not is_stopped[0]:
                        return o.send(3)
                scheduler.schedule_relative(600, action1)

                def action2(scheduler, state):
                    if not is_stopped[0]:
                        return o.send(4)
                scheduler.schedule_relative(700, action2)

                def action3(scheduler, state):
                    if not is_stopped[0]:
                        return o.send(5)
                scheduler.schedule_relative(900, action3)

                def action4(scheduler, state):
                    if not is_stopped[0]:
                        return o.send(6)
                scheduler.schedule_relative(1100, action4)

                def dispose():
                    is_stopped[0] = True
                return dispose
            return Observable.create(subscribe)

        results = scheduler.start(create)
        assert results.messages == [send(200, 1), send(200, 2), send(800, 3), send(900, 4)]

    def test_create_observer_throws(self):
        def subscribe(o, observer=None):
            o.send(1)
            return lambda: None

        with self.assertRaises(RxException):
            Observable.create(subscribe).subscribe_(lambda x: _raise('ex'))

        def subscribe2(o):
            o.throw('exception')
            return lambda: None

        with self.assertRaises(RxException):
            Observable.create(subscribe2).subscribe_(throw=lambda ex: _raise('ex'))

        def subscribe3(o):
            o.close()
            return lambda: None

        with self.assertRaises(RxException):
            Observable.create(subscribe3).subscribe_(close=lambda: _raise('ex'))

    def test_create_next(self):
        scheduler = TestScheduler()
        def create():
            def subscribe(o, observer=None):
                o.send(1)
                o.send(2)
                return Disposable.empty()
            return Observable.create(subscribe)
        results = scheduler.start(create)

        assert results.messages == [send(200, 1), send(200, 2)]

    def test_create_completed(self):
        scheduler = TestScheduler()
        def create():
            def subscribe(o, observer=None):
                o.close()
                o.send(100)
                o.throw('ex')
                o.close()
                return Disposable.empty()
            return Observable.create(subscribe)

        results = scheduler.start(create)
        assert results.messages == [close(200)]

    def test_create_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        def create():
            def subscribe(o, observer=None):
                o.throw(ex)
                o.send(100)
                o.throw('foo')
                o.close()
                return Disposable.empty()

            return Observable.create(subscribe)
        results = scheduler.start(create)

        assert results.messages == [throw(200, ex)]

    def test_create_exception(self):
        with self.assertRaises(RxException):
            Observable.create(lambda: o, _raise('ex')).subscribe()

    def test_create_dispose(self):
        scheduler = TestScheduler()

        def create():
            def subscribe(o, observer=None):
                d = BooleanDisposable()
                o.send(1)
                o.send(2)

                def action1(scheduler, state):
                    if not d.is_disposed:
                        o.send(3)
                scheduler.schedule_relative(600, action1)

                def action2(scheduler, state):
                    if not d.is_disposed:
                        o.send(4)
                scheduler.schedule_relative(700, action2)

                def action3(scheduler, state):
                    if not d.is_disposed:
                        o.send(5)
                scheduler.schedule_relative(900, action3)

                def action4(scheduler, state):
                    if not d.is_disposed:
                        o.send(6)
                scheduler.schedule_relative(1100, action4)

                return d
            return Observable.create(subscribe)

        results = scheduler.start(create)

        assert results.messages == [send(200, 1), send(200, 2), send(800, 3), send(900, 4)]


    def test_create_observer_throws(self):
        def subscribe1(o):
            o.send(1)
            return Disposable.empty()

        def send(x):
            _raise('ex')

        with self.assertRaises(RxException):
            Observable.create(subscribe1).subscribe_(send)

        def subscribe2(o):
            o.throw('exception')
            return Disposable.empty()

        with self.assertRaises(RxException):
            Observable.create(subscribe2).subscribe_(throw=lambda ex: _raise('ex'))

        def subscribe3(o):
            o.close()
            return Disposable.empty()

        with self.assertRaises(RxException):
            Observable.create(subscribe3).subscribe_(close=_raise('ex'))

