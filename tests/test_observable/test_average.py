import unittest

from rx import operators as _
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
        res = scheduler.start(create=lambda: xs.pipe(_.average())).messages

        assert(len(res) == 1)
        assert(res[0].value.kind == 'E' and res[0].value.exception != None)
        assert(res[0].time == 250)

    def test_average_int32_return(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.average())

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, 2.0), on_completed(250)]

    def test_average_int32_some(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_next(210, 3), on_next(220, 4),
                on_next(230, 2), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.average())

        res = scheduler.start(create=create).messages
        assert res == [on_next(250, 3.0), on_completed(250)]

    def test_average_int32_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_error(210, ex)]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.pipe(_.average())

        res = scheduler.start(create=create).messages
        assert res == [on_error(210, ex)]

    def test_average_int32_never(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.pipe(_.average())

        res = scheduler.start(create=create).messages
        assert res == []

    def test_average_mapper_regular_int32(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(210, "b"), on_next(220, "fo"),
                on_next(230, "qux"), on_completed(240),
                )

        def create():
            return xs.pipe(_.average(len))

        res = scheduler.start(create=create)

        assert res.messages == [on_next(240, 2.0), on_completed(240)]
        assert xs.subscriptions == [subscribe(200, 240)]
