import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestBufferWithCount(unittest.TestCase):
    def test_buffer_with_time_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(100, 1),
            send(210, 2),
            send(240, 3),
            send(281, 4),
            send(321, 5),
            send(351, 6),
            send(381, 7),
            send(421, 8),
            send(471, 9),
            close(600))

        def create():
            return xs.buffer_with_time(100, 70).map(lambda x: ",".join([str(a) for a in x]))

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(301, "2,3,4"),
            send(371, "4,5,6"),
            send(441, "6,7,8"),
            send(511, "8,9"),
            send(581, ""),
            send(601, ""),
            close(601))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_buffer_with_time_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(100, 1),
            send(210, 2),
            send(240, 3),
            send(280, 4),
            send(320, 5),
            send(350, 6),
            send(380, 7),
            send(420, 8),
            send(470, 9),
            throw(600, ex))

        def create():
            return xs.buffer_with_time(100, 70).map(lambda x: ",".join([str(a) for a in x]))

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(301, "2,3,4"),
            send(371, "4,5,6"),
            send(441, "6,7,8"),
            send(511, "8,9"),
            send(581, ""),
            throw(600, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_buffer_with_time_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(100, 1),
            send(210, 2),
            send(240, 3),
            send(281, 4),
            send(321, 5),
            send(351, 6),
            send(381, 7),
            send(421, 8),
            send(471, 9),
            close(600))

        def create():
            return xs.buffer_with_time(100, 70).map(lambda x: ",".join([str(a) for a in x]))

        results = scheduler.start(create, disposed=370)
        results.messages.assert_equal(send(301, "2,3,4"))
        xs.subscriptions.assert_equal(subscribe(200, 370))

    def test_buffer_with_time_basic_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(100, 1),
            send(210, 2),
            send(240, 3),
            send(280, 4),
            send(320, 5),
            send(350, 6),
            send(380, 7),
            send(420, 8),
            send(470, 9),
            close(600))

        def create():
            return xs.buffer_with_time(100).map(lambda x: ",".join([str(a) for a in x]))

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(301, "2,3,4"),
            send(401, "5,6,7"),
            send(501, "8,9"),
            send(601, ""),
            close(601))
        xs.subscriptions.assert_equal(subscribe(200, 600))
