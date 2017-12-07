import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestPairwise(unittest.TestCase):

    def test_pairwise_empty(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            close(210)
        )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)

        results.messages.assert_equal(
            close(210)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 210)
        )

    def test_pairwise_single(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            close(220)
        )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)


        results.messages.assert_equal(
            close(220)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 220)
        )


    def test_pairwise_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            send(290, 2),
            send(350, 1),
            close(360)
        )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(240, (4,3)),
            send(290, (3, 2)),
            send(350, (2, 1)),
            close(360)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 360)
         )


    def test_pairwise_not_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            send(290, 2),
            send(350, 1)
          )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)


        results.messages.assert_equal(
            send(240, (4,3)),
            send(290, (3, 2)),
            send(350, (2, 1))
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )


    def test_pairwise_error(self):
        error = Exception()
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            throw(290, error),
            send(350, 1),
            close(360)
          )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)


        results.messages.assert_equal(
            send(240, (4,3)),
            throw(290, error)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 290)
        )

    def test_pairwise_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            send(290, 2),
            send(350, 1),
            close(360)
          )

        def create():
            return xs.pairwise()

        results = scheduler.start(create, disposed=280)

        results.messages.assert_equal(
            send(240, (4,3))
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 280)
        )
