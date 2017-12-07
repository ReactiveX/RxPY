import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestObserveOn(unittest.TestCase):

    def test_observe_on_normal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                            send(150, 1),
                            send(210, 2),
                            close(250)
                        )

        def create():
            return xs.observe_on(scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(send(211, 2), close(251))
        xs.subscriptions.assert_equal(subscribe(200, 251))

    def test_observe_throw(self):
        scheduler = TestScheduler()
        ex = 'ex'

        xs = scheduler.create_hot_observable(
                            send(150, 1),
                            throw(210, ex)
                        )

        def create():
            return xs.observe_on(scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(throw(211, ex))
        xs.subscriptions.assert_equal(subscribe(200, 211))


    def test_observe_on_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                            send(150, 1),
                            close(250)
                        )

        def create():
            return xs.observe_on(scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(close(251))
        xs.subscriptions.assert_equal(subscribe(200, 251))


    def test_observe_on_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                            send(150, 1)
                        )

        def create():
            return xs.observe_on(scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

