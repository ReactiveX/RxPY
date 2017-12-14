import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSome(unittest.TestCase):

    def test_some_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some()

        res = scheduler.start(create=create).messages
        assert res == [send(250, False), close(250)]

    def test_some_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some()

        res = scheduler.start(create=create).messages
        assert res == [send(210, True), close(210)]

    def test_some_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some()
        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_some_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some()

        res = scheduler.start(create=create).messages
        assert res == []

    def test_some_predicate_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        assert res == [send(250, False), close(250)]

    def test_some_predicate_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        assert res == [send(210, True), close(210)]

    def test_some_predicate_return_not_match(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, -2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        assert res == [send(250, False), close(250)]

    def test_some_predicate_some_none_match(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, -2), send(220, -3), send(230, -4), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        assert res == [send(250, False), close(250)]

    def test_some_predicate_some_match(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, -2), send(220, 3), send(230, -4), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        assert res == [send(220, True), close(220)]

    def test_some_predicate_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)
        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_some_predicate_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.some(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        assert res == []
