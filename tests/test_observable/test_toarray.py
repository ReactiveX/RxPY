import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestToArray(unittest.TestCase):

    def test_toiterable_completed(self):
        scheduler = TestScheduler()
        msgs = [on_next(110, 1), on_next(220, 2), on_next(330, 3), on_next(440, 4), on_next(550, 5), on_completed(660)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.to_iterable()
        results = scheduler.start(create=create).messages
        assert(len(results) == 2)
        assert(results[0].time == 660)
        assert(results[0].value.kind == 'N')
        assert(results[0].value.value == [2, 3, 4, 5])
        assert(on_completed(660).equals(results[1]))
        xs.subscriptions.assert_equal(subscribe(200, 660))

    def test_toiterableerror(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [on_next(110, 1), on_next(220, 2), on_next(330, 3), on_next(440, 4), on_next(550, 5), on_error(660, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.to_iterable()
        results = scheduler.start(create=create).messages
        results.assert_equal(on_error(660, ex))
        xs.subscriptions.assert_equal(subscribe(200, 660))

    def test_toiterabledisposed(self):
        scheduler = TestScheduler()
        msgs = [on_next(110, 1), on_next(220, 2), on_next(330, 3), on_next(440, 4), on_next(550, 5)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
           return xs.to_iterable()

        results = scheduler.start(create=create).messages
        results.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))
