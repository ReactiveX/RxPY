import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestPairwise(unittest.TestCase):

    def test_pairwise_empty(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_completed(210)
        )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_completed(210)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 210)
        )

    def test_pairwise_single(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_completed(220)
        )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)


        results.messages.assert_equal(
            on_completed(220)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 220)
        )


    def test_pairwise_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(240, 3),
            on_next(290, 2),
            on_next(350, 1),
            on_completed(360)
        )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(240, (4,3)),
            on_next(290, (3, 2)),
            on_next(350, (2, 1)),
            on_completed(360)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 360)
         )


    def test_pairwise_not_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(240, 3),
            on_next(290, 2),
            on_next(350, 1)
          )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)


        results.messages.assert_equal(
            on_next(240, (4,3)),
            on_next(290, (3, 2)),
            on_next(350, (2, 1))
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )


    def test_pairwise_error(self):
        error = Exception()
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(240, 3),
            on_error(290, error),
            on_next(350, 1),
            on_completed(360)
          )

        def create():
            return xs.pairwise()

        results = scheduler.start(create)


        results.messages.assert_equal(
            on_next(240, (4,3)),
            on_error(290, error)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 290)
        )

    def test_pairwise_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, 5),
            on_next(210, 4),
            on_next(240, 3),
            on_next(290, 2),
            on_next(350, 1),
            on_completed(360)
          )

        def create():
            return xs.pairwise()

        results = scheduler.start(create, disposed=280)

        results.messages.assert_equal(
            on_next(240, (4,3))
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 280)
        )
