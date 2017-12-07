import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestToArray(unittest.TestCase):

    def test_toiterable_completed(self):
        scheduler = TestScheduler()
        msgs = [send(110, 1), send(220, 2), send(330, 3), send(440, 4), send(550, 5), close(660)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.to_iterable()
        results = scheduler.start(create=create).messages
        assert(len(results) == 2)
        assert(results[0].time == 660)
        assert(results[0].value.kind == 'N')
        assert(results[0].value.value == [2, 3, 4, 5])
        assert(close(660).equals(results[1]))
        xs.subscriptions.assert_equal(subscribe(200, 660))

    def test_toiterableerror(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(110, 1), send(220, 2), send(330, 3), send(440, 4), send(550, 5), throw(660, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.to_iterable()
        results = scheduler.start(create=create).messages
        results.assert_equal(throw(660, ex))
        xs.subscriptions.assert_equal(subscribe(200, 660))

    def test_toiterabledisposed(self):
        scheduler = TestScheduler()
        msgs = [send(110, 1), send(220, 2), send(330, 3), send(440, 4), send(550, 5)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.to_iterable()

        results = scheduler.start(create=create).messages
        results.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))
