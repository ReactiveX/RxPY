import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestBuffer(unittest.TestCase):

    def test_buffer_boundaries_simple(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(90, 1),
            send(180, 2),
            send(250, 3),
            send(260, 4),
            send(310, 5),
            send(340, 6),
            send(410, 7),
            send(420, 8),
            send(470, 9),
            send(550, 10),
            close(590)
        )

        ys = scheduler.create_hot_observable(
            send(255, True),
            send(330, True),
            send(350, True),
            send(400, True),
            send(500, True),
            close(900)
        )

        def create():
            return xs.buffer(ys)

        res = scheduler.start(create=create)

        assert [
            send(255, lambda b: b == [3]),
            send(330, lambda b: b == [4, 5]),
            send(350, lambda b: b == [6]),
            send(400, lambda b: b == []),
            send(500, lambda b: b == [7, 8, 9]),
            send(590, lambda b: b == [10]),
            close(590)] == res.messages

        assert xs.subscriptions == [
            subscribe(200, 590)]

        assert ys.subscriptions == [
            subscribe(200, 590)]

    def test_buffer_boundaries_closeboundaries(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(90, 1),
            send(180, 2),
            send(250, 3),
            send(260, 4),
            send(310, 5),
            send(340, 6),
            send(410, 7),
            send(420, 8),
            send(470, 9),
            send(550, 10),
            close(590)
        )

        ys = scheduler.create_hot_observable(
            send(255, True),
            send(330, True),
            send(350, True),
            close(400)
        )

        def create():
            return xs.buffer(ys)

        res = scheduler.start(create=create)

        assert [
            send(255, lambda b: b == [3]),
            send(330, lambda b: b == [4, 5]),
            send(350, lambda b: b == [6]),
            send(400, lambda b: b == []),
            close(400)] == res.messages

        assert xs.subscriptions == [
            subscribe(200, 400)]

        assert ys.subscriptions == [
            subscribe(200, 400)]

    def test_buffer_boundaries_throwsource(self):
        ex = 'ex'

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(90, 1),
            send(180, 2),
            send(250, 3),
            send(260, 4),
            send(310, 5),
            send(340, 6),
            send(380, 7),
            throw(400, ex)
        )

        ys = scheduler.create_hot_observable(
            send(255, True),
            send(330, True),
            send(350, True),
            close(500)
        )

        def create():
            return xs.buffer(ys)

        res = scheduler.start(create=create)

        assert [
            send(255, lambda b: b == [3]),
            send(330, lambda b: b == [4, 5]),
            send(350, lambda b: b == [6]),
            throw(400, ex)] == res.messages

        assert xs.subscriptions == [
            subscribe(200, 400)]

        assert ys.subscriptions == [
            subscribe(200, 400)]

    def test_buffer_boundaries_throwboundaries(self):
        ex = 'ex'

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(90, 1),
            send(180, 2),
            send(250, 3),
            send(260, 4),
            send(310, 5),
            send(340, 6),
            send(410, 7),
            send(420, 8),
            send(470, 9),
            send(550, 10),
            close(590)
        )

        ys = scheduler.create_hot_observable(
            send(255, True),
            send(330, True),
            send(350, True),
            throw(400, ex)
        )

        def create():
            return xs.buffer(ys)
        res = scheduler.start(create=create)

        assert [
            send(255, lambda b: b == [3]),
            send(330, lambda b: b == [4, 5]),
            send(350, lambda b: b == [6]),
            throw(400, ex)] == res.messages

        assert xs.subscriptions == [
            subscribe(200, 400)]

        assert ys.subscriptions == [
            subscribe(200, 400)]
