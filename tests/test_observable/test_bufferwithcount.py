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
    def test_buffer_with_count_basic(self):
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
            return xs.buffer_with_count(3, 2).map(lambda x: str(x))

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(280, str([2,3,4])),
            send(350, str([4,5,6])),
            send(420, str([6,7,8])),
            send(600, str([8,9])),
            close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_buffer_with_count_disposed(self):
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
            return xs.buffer_with_count(3, 2).map(lambda x: str(x))

        results = scheduler.start(create, disposed=370)

        results.messages.assert_equal(send(280, str([2, 3, 4])),
        send(350, str([4, 5, 6])))
        xs.subscriptions.assert_equal(subscribe(200, 370))


