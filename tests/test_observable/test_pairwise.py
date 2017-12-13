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

        assert results.messages == [
            close(210)]

        assert xs.subscriptions == [
            subscribe(200, 210)]

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

        assert results.messages == [close(220)]
        assert xs.subscriptions == [subscribe(200, 220)]

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

        assert results.messages == [
            send(240, (4, 3)),
            send(290, (3, 2)),
            send(350, (2, 1)),
            close(360)]

        assert xs.subscriptions == [subscribe(200, 360)]

    def test_pairwise_not_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            send(290, 2),
            send(350, 1))

        def create():
            return xs.pairwise()

        results = scheduler.start(create)

        assert results.messages == [
            send(240, (4, 3)),
            send(290, (3, 2)),
            send(350, (2, 1))]

        assert xs.subscriptions == [
            subscribe(200, 1000)]

    def test_pairwise_error(self):
        error = Exception()
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            throw(290, error),
            send(350, 1),
            close(360))

        def create():
            return xs.pairwise()

        results = scheduler.start(create)

        assert results.messages == [
            send(240, (4, 3)),
            throw(290, error)]

        assert xs.subscriptions == [
            subscribe(200, 290)]

    def test_pairwise_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            send(290, 2),
            send(350, 1),
            close(360))

        def create():
            return xs.pairwise()

        results = scheduler.start(create, disposed=280)

        assert results.messages == [
            send(240, (4, 3))]

        assert xs.subscriptions == [
            subscribe(200, 280)]
