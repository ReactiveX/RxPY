import unittest

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


class TestThrottleFirst(unittest.TestCase):

    def test_throttle_first_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(250, 3),
            on_next(310, 4),
            on_next(350, 5),
            on_next(410, 6),
            on_next(450, 7),
            on_completed(500)
        )

        def create():
            return xs.throttle_first(200, scheduler)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(410, 6),
            on_completed(500)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 500)
        )

    def test_throttle_first_never(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
          on_next(150, 1)
        )

        def create():
            return xs.throttle_first(200, scheduler)

        results = scheduler.start(create=create)


        results.messages.assert_equal()

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )


    def test_throttle_first_empty(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_completed(500)
        )


        def create():
            return xs.throttle_first(200, scheduler)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
            on_completed(500)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 500)
        )

    def test_throttle_first_error(self):
        error = RxException()

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
          on_next(150, 1),
          on_next(210, 2),
          on_next(250, 3),
          on_next(310, 4),
          on_next(350, 5),
          on_error(410, error),
          on_next(450, 7),
          on_completed(500)
        )

        def create():
            return xs.throttle_first(200, scheduler)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
          on_next(210, 2),
          on_error(410, error)
        )

        xs.subscriptions.assert_equal(
          subscribe(200, 410)
        )


    def test_throttle_first_no_end(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(150, 1),
            on_next(210, 2),
            on_next(250, 3),
            on_next(310, 4),
            on_next(350, 5),
            on_next(410, 6),
            on_next(450, 7)
        )

        def create():
            return xs.throttle_first(200, scheduler)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(410, 6)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )

