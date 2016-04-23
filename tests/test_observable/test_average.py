import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestAverage(unittest.TestCase):

    def test_average_int32_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)
        res = scheduler.start(create=lambda: xs.average()).messages

        assert(len(res) == 1)
        assert(res[0].value.kind == 'E' and res[0].value.exception != None)
        assert(res[0].time == 250)

    def test_average_int32_return(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.average()

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, 2.0), on_completed(250))

    def test_average_int32_some(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 3), on_next(220, 4), on_next(230, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.average()

        res = scheduler.start(create=create).messages
        res.assert_equal(on_next(250, 3.0), on_completed(250))

    def test_average_int32_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_error(210, ex)]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.average()

        res = scheduler.start(create=create).messages
        res.assert_equal(on_error(210, ex))

    def test_average_int32_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.average()

        res = scheduler.start(create=create).messages
        res.assert_equal()

    def test_average_selector_regular_int32(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, "b"), on_next(220, "fo"), on_next(230, "qux"), on_completed(240))

        def create():
            return xs.average(lambda x: len(x))

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(240, 2.0), on_completed(240))
        xs.subscriptions.assert_equal(subscribe(200, 240))
