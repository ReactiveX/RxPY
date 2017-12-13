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
    def test_buffer_with_time_or_count_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(205, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(370, 7), send(420, 8), send(470, 9), close(600))

        def create():
            return xs.buffer_with_time_or_count(70, 3).map(lambda x: ",".join([str(a) for a in x]))

        results = scheduler.start(create)

        results.messages.assert_equal(send(240, "1,2,3"), send(310, "4"), send(370, "5,6,7"), send(440, "8"), send(510, "9"), send(580, ""), send(600, ""), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_buffer_with_time_or_count_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(205, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(370, 7), send(420, 8), send(470, 9), throw(600, ex))

        def create():
            return xs.buffer_with_time_or_count(70, 3).map(lambda x: ",".join([str(a) for a in x]))

        results = scheduler.start(create)
        results.messages.assert_equal(send(240, "1,2,3"), send(310, "4"), send(370, "5,6,7"), send(440, "8"), send(510, "9"), send(580, ""), throw(600, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_buffer_with_time_or_count_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(205, 1), send(210, 2), send(240, 3), send(280, 4), send(320, 5), send(350, 6), send(370, 7), send(420, 8), send(470, 9), close(600))

        def create():
            return xs.buffer_with_time_or_count(70, 3).map(lambda x: ",".join([str(a) for a in x]))

        results = scheduler.start(create, disposed=370)
        results.messages.assert_equal(
            send(240, "1,2,3"),
            send(310, "4"),
            #send(370, "5,6,7")
            )
        xs.subscriptions.assert_equal(subscribe(200, 370))
