import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestTakeLastBuffer(unittest.TestCase):

    def test_take_last_buffer_zero_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))

        def create():
            return xs.take_last_buffer(0)

        res = scheduler.start(create)

        def predicate(lst):
            return len(lst) == 0

        res.messages.assert_equal(on_next(650, predicate), on_completed(650))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_take_last_buffer_zero_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))

        def create():
            return xs.take_last_buffer(0)

        res = scheduler.start(create)

        res.messages.assert_equal(on_error(650, ex))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_take_last_buffer_zero_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))

        def create():
            return xs.take_last_buffer(0)

        res = scheduler.start(create)

        res.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_take_last_buffer_one_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))

        def create():
            return xs.take_last_buffer(1)

        res = scheduler.start(create)

        def predicate(lst):
            return lst == [9]

        res.messages.assert_equal(on_next(650, predicate), on_completed(650))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_take_last_buffer_one_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))

        def create():
            return xs.take_last_buffer(1)

        res = scheduler.start(create)

        res.messages.assert_equal(on_error(650, ex))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_take_last_buffer_one_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))

        def create():
            return xs.take_last_buffer(1)

        res = scheduler.start(create)

        res.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_take_last_buffer_three_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))

        def create():
            return xs.take_last_buffer(3)

        res = scheduler.start(create)

        def predicate(lst):
            return lst == [7, 8, 9]

        res.messages.assert_equal(on_next(650, predicate), on_completed(650))
        xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_Take_last_buffer_Three_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     res = scheduler.start(create)
#         return xs.take_last_buffer(3)

#     res.messages.assert_equal(on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_Take_last_buffer_Three_Disposed():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     res = scheduler.start(create)
#         return xs.take_last_buffer(3)

#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

