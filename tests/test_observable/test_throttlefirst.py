import unittest

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


class TestThrottleFirst(unittest.TestCase):

    def test_throttle_first_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(250, 3),
            send(310, 4),
            send(350, 5),
            send(410, 6),
            send(450, 7),
            close(500)
        )

        def create():
            return xs.throttle_first(200)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
            send(210, 2),
            send(410, 6),
            close(500)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 500)
        )

    def test_throttle_first_never(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
          send(150, 1)
        )

        def create():
            return xs.throttle_first(200)

        results = scheduler.start(create=create)


        results.messages.assert_equal()

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )


    def test_throttle_first_empty(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            close(500)
        )


        def create():
            return xs.throttle_first(200)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
            close(500)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 500)
        )

    def test_throttle_first_error(self):
        error = RxException()

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
          send(150, 1),
          send(210, 2),
          send(250, 3),
          send(310, 4),
          send(350, 5),
          throw(410, error),
          send(450, 7),
          close(500)
        )

        def create():
            return xs.throttle_first(200)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
          send(210, 2),
          throw(410, error)
        )

        xs.subscriptions.assert_equal(
          subscribe(200, 410)
        )


    def test_throttle_first_no_end(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(250, 3),
            send(310, 4),
            send(350, 5),
            send(410, 6),
            send(450, 7)
        )

        def create():
            return xs.throttle_first(200)

        results = scheduler.start(create=create)

        results.messages.assert_equal(
            send(210, 2),
            send(410, 6)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )

