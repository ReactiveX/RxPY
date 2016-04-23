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


class TestDefer(unittest.TestCase):
    def test_defer_complete(self):
        xs = [None]
        invoked = [0]
        scheduler = TestScheduler()

        def create():
            def defer():
                invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(
                                    on_next(100, scheduler.clock),
                                    on_completed(200)
                                )
                return xs[0]
            return Observable.defer(defer)
        results = scheduler.start(create)
        results.messages.assert_equal(
                            on_next(300, 200),
                            on_completed(400)
                        )
        assert(1 == invoked[0])
        return xs[0].subscriptions.assert_equal(subscribe(200, 400))

    def test_defer_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = [None]
        ex = 'ex'

        def create():
            def defer():
                invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_error(200, ex))
                return xs[0]
            return Observable.defer(defer)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(300, 200), on_error(400, ex))
        assert (1 == invoked[0])
        return xs[0].subscriptions.assert_equal(subscribe(200, 400))

    def test_defer_dispose(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = [None]

        def create():
            def defer():
                invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_next(200, invoked[0]), on_next(1100, 1000))
                return xs[0]
            return Observable.defer(defer)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(300, 200), on_next(400, 1))
        assert(1 == invoked[0])
        return xs[0].subscriptions.assert_equal(subscribe(200, 1000))

    def test_defer_throw(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'

        def create():
            def defer():
                invoked[0] += 1
                raise Exception(ex)

            return Observable.defer(defer)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(200, ex))
        assert(1 == invoked[0])
