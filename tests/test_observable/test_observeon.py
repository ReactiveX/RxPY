import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestObserveOn(unittest.TestCase):

    def test_observe_on_normal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                            on_next(150, 1),
                            on_next(210, 2),
                            on_completed(250)
                        )

        def create():
            return xs.observe_on(scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(211, 2), on_completed(251))
        xs.subscriptions.assert_equal(subscribe(200, 251))

    def test_observe_on_error(self):
        scheduler = TestScheduler()
        ex = 'ex'

        xs = scheduler.create_hot_observable(
                            on_next(150, 1),
                            on_error(210, ex)
                        )

        def create():
            return xs.observe_on(scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_error(211, ex))
        xs.subscriptions.assert_equal(subscribe(200, 211))


    def test_observe_on_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                            on_next(150, 1),
                            on_completed(250)
                        )

        def create():
            return xs.observe_on(scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(251))
        xs.subscriptions.assert_equal(subscribe(200, 251))


    def test_observe_on_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                            on_next(150, 1)
                        )

        def create():
            return xs.observe_on(scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

