import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestTakeLastBuffer(unittest.TestCase):

    def test_take_last_buffer_zero_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.take_last_buffer(0)

        res = scheduler.start(create)

        def predicate(lst):
            return len(lst) == 0

        assert res.messages == [send(650, predicate), close(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_take_last_buffer_zero_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))

        def create():
            return xs.take_last_buffer(0)

        res = scheduler.start(create)

        assert res.messages == [throw(650, ex)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_take_last_buffer_zero_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))

        def create():
            return xs.take_last_buffer(0)

        res = scheduler.start(create)

        assert res.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_take_last_buffer_one_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.take_last_buffer(1)

        res = scheduler.start(create)

        def predicate(lst):
            return lst == [9]

        assert res.messages == [send(650, predicate), close(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_take_last_buffer_one_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))

        def create():
            return xs.take_last_buffer(1)

        res = scheduler.start(create)

        assert res.messages == [throw(650, ex)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_take_last_buffer_one_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))

        def create():
            return xs.take_last_buffer(1)

        res = scheduler.start(create)

        assert res.messages == []
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_take_last_buffer_three_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.take_last_buffer(3)

        res = scheduler.start(create)

        def predicate(lst):
            return lst == [7, 8, 9]

        assert res.messages == [send(650, predicate), close(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

# def test_Take_last_buffer_Three_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))
#     res = scheduler.start(create)
#         return xs.take_last_buffer(3)

#     assert res.messages == [throw(650, ex)]
#     assert xs.subscriptions == [subscribe(200, 650)]

# def test_Take_last_buffer_Three_Disposed():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))
#     res = scheduler.start(create)
#         return xs.take_last_buffer(3)

#     assert res.messages == []
#     assert xs.subscriptions == [subscribe(200, 1000)]

