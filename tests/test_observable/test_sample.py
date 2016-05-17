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


class TestSample(unittest.TestCase):

    def test_sample_regular(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_next(380, 7), on_completed(390))

        def create():
            return xs.sample(50, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(250, 3), on_next(300, 5), on_next(350, 6), on_next(400, 7), on_completed(400))

    def test_sample_error_in_flight(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(310, 6), on_error(330, ex))

        def create():
            return xs.sample(50, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(250, 3), on_next(300, 5), on_error(330, ex))

    def test_sample_empty(self):
        scheduler = TestScheduler()

        def create():
            return Observable.empty(scheduler=scheduler).sample(0, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(201))

    def test_sample_error(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.throw_exception(ex, scheduler=scheduler).sample(0, scheduler=scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(201, ex))

    def test_sample_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().sample(0, scheduler=scheduler)
        results = scheduler.start(create)
        results.messages.assert_equal()
