import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.operators.observable.concat import concat

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


class TestConcat(unittest.TestCase):
    def test_concat_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(close(251))

    def test_concat_empty_never(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = Observable.never()

        def create():
            return e1.concat(e2)
        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_concat_never_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = Observable.never()

        def create():
            return e2.concat(e1)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_concat_never_never(self):
        scheduler = TestScheduler()
        e1 = Observable.never()
        e2 = Observable.never()

        def create():
            return e1.concat(e2)
        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_concat_empty_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), throw(250, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(250, ex))

    def test_concat_throw_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), throw(230, ex)]
        msgs2 = [send(150, 1), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(230, ex))

    def test_concat_throw_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), throw(230, ex)]
        msgs2 = [send(150, 1), throw(250, 'ex2')]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(230, ex))

    def test_concat_return_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(230)]
        msgs2 = [send(150, 1), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2), close(251))

    def test_concat_empty_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), send(240, 2), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(send(240, 2), close(251))

    def test_concat_return_never(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = Observable.never()

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2))

    def test_concat_never_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = Observable.never()

        def create():
            return e2.concat(e1)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_concat_return_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(220, 2), close(230)]
        msgs2 = [send(150, 1), send(240, 3), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(send(220, 2), send(240, 3), close(251))

    def test_concat_throw_return(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), throw(230, ex)]
        msgs2 = [send(150, 1), send(240, 2), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(230, ex))

    def test_concat_return_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(220, 2), close(230)]
        msgs2 = [send(150, 1), throw(250, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(send(220, 2), throw(250, ex))

    def test_concat_some_data_some_data(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(220, 3), close(225)]
        msgs2 = [send(150, 1), send(230, 4), send(240, 5), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(251))
