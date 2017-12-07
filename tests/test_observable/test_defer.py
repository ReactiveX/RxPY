import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

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


class TestDefer(unittest.TestCase):
    def test_defer_complete(self):
        xs = [None]
        invoked = [0]
        scheduler = TestScheduler()

        def create():
            def defer():
                invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(
                                    send(100, scheduler.clock),
                                    close(200)
                                )
                return xs[0]
            return Observable.defer(defer)
        results = scheduler.start(create)
        results.messages.assert_equal(
                            send(300, 200),
                            close(400)
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
                xs[0] = scheduler.create_cold_observable(send(100, scheduler.clock), throw(200, ex))
                return xs[0]
            return Observable.defer(defer)

        results = scheduler.start(create)

        results.messages.assert_equal(send(300, 200), throw(400, ex))
        assert (1 == invoked[0])
        return xs[0].subscriptions.assert_equal(subscribe(200, 400))

    def test_defer_dispose(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = [None]

        def create():
            def defer():
                invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(send(100, scheduler.clock), send(200, invoked[0]), send(1100, 1000))
                return xs[0]
            return Observable.defer(defer)

        results = scheduler.start(create)
        results.messages.assert_equal(send(300, 200), send(400, 1))
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

        results.messages.assert_equal(throw(200, ex))
        assert(1 == invoked[0])
