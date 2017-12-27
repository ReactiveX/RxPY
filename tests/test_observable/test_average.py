import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestAverage(unittest.TestCase):

    def test_average_int32_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)
        res = scheduler.start(create=lambda: xs.average()).messages

        assert(len(res) == 1)
        assert(res[0].value.kind == 'E' and res[0].value.exception != None)
        assert(res[0].time == 250)

    def test_average_int32_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.average()

        res = scheduler.start(create=create).messages
        assert res == [send(250, 2.0), close(250)]

    def test_average_int32_some(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 3), send(220, 4), send(230, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.average()

        res = scheduler.start(create=create).messages
        assert res == [send(250, 3.0), close(250)]

    def test_average_int32_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(210, ex)]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.average()

        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_average_int32_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.average()

        res = scheduler.start(create=create).messages
        assert res == []

    def test_average_mapper_regular_int32(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, "b"), send(220, "fo"), send(230, "qux"), close(240))

        def create():
            return xs.average(lambda x: len(x))

        res = scheduler.start(create=create)

        assert res.messages == [send(240, 2.0), close(240)]
        assert xs.subscriptions == [subscribe(200, 240)]
