import unittest

from rx import Observable
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


class TestConcat(unittest.TestCase):
    def test_concat_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(250))

    def test_concat_empty_never(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = Observable.never()

        def create():
            return e1.concat(e2)
        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_concat_never_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
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
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(250, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(250, ex))

    def test_concat_throw_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex)]
        msgs2 = [on_next(150, 1), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(230, ex))

    def test_concat_throw_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex)]
        msgs2 = [on_next(150, 1), on_error(250, 'ex2')]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)
        results = scheduler.start(create)
        results.messages.assert_equal(on_error(230, ex))

    def test_concat_return_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2), on_completed(250))

    def test_concat_empty_return(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(240, 2), on_completed(250))

    def test_concat_return_never(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = Observable.never()

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2))

    def test_concat_never_return(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = Observable.never()

        def create():
            return e2.concat(e1)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_concat_return_return(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_next(240, 3), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(220, 2), on_next(240, 3), on_completed(250))

    def test_concat_throw_return(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex)]
        msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(230, ex))

    def test_concat_return_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(250, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(220, 2), on_error(250, ex))

    def test_concat_some_data_some_data(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(225)]
        msgs2 = [on_next(150, 1), on_next(230, 4), on_next(240, 5), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.concat(e2)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
