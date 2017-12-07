import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestToDict(unittest.TestCase):

    def test_to_set_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(110, 1),
            send(220, 2),
            send(330, 3),
            send(440, 4),
            send(550, 5),
            close(660)
        )

        def create():
            return xs.to_set()

        results = scheduler.start(create)
        results.messages.assert_equal(
            send(660, set([2,3,4,5])),
            close(660)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 660)
        )


    def test_to_set_error(self):
        error = Exception()

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(110, 1),
            send(220, 2),
            send(330, 3),
            send(440, 4),
            send(550, 5),
            throw(660, error)
        )

        results = scheduler.start(lambda: xs.to_set())

        results.messages.assert_equal(
            throw(660, error)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 660)
        )

    def test_to_set_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(110, 1),
            send(220, 2),
            send(330, 3),
            send(440, 4),
            send(550, 5)
        )

        results = scheduler.start(lambda: xs.to_set())

        results.messages.assert_equal()

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )
