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


class TestSample(unittest.TestCase):

    def test_sample_regular(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(230, 3), send(260, 4), send(300, 5), send(350, 6), send(380, 7), close(390))

        def create():
            return xs.sample(50, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(send(250, 3), send(300, 5), send(350, 6), send(400, 7), close(400))

    def test_sample_error_in_flight(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(230, 3), send(260, 4), send(300, 5), send(310, 6), throw(330, ex))

        def create():
            return xs.sample(50, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(send(250, 3), send(300, 5), throw(330, ex))

    def test_sample_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.empty(scheduler=scheduler).sample(0, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(close(201))

    def test_sample_error(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.throw_exception(ex, scheduler=scheduler).sample(0, scheduler=scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(throw(201, ex))

    def test_sample_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().sample(0, scheduler=scheduler)
        results = scheduler.start(create)
        results.messages.assert_equal()
