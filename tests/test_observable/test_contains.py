import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestContains(unittest.TestCase):

    def test_contains_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(42)
        res = scheduler.start(create=create).messages
        assert res == [send(250, False), close(250)]

    def test_contains_return_positive(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(2)

        res = scheduler.start(create=create).messages
        assert res == [send(210, True), close(210)]

    def test_contains_return_negative(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(-2)

        res = scheduler.start(create=create).messages
        assert res == [send(250, False), close(250)]

    def test_contains_some_positive(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), send(220, 3), send(230, 4), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(3)

        res = scheduler.start(create=create).messages
        assert res == [send(220, True), close(220)]

    def test_contains_some_negative(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), send(220, 3), send(230, 4), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(-3)
        res = scheduler.start(create=create).messages
        assert res == [send(250, False), close(250)]

    def test_contains_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(210, ex))

        def create():
            return xs.contains(42)

        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_contains_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.contains(42)

        res = scheduler.start(create=create).messages
        assert res == []

    def test_contains_comparer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2))

        def create():
            def comparer(a, b):
                raise Exception(ex)

            return xs.contains(42, comparer)

        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_contains_comparer_contains_value(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 3), send(220, 4), send(230, 8), close(250))

        def create():
            return xs.contains(42, lambda a, b: a % 2 == b % 2)

        res = scheduler.start(create=create).messages
        assert res == [send(220, True), close(220)]

    def test_contains_comparer_does_not_contain_value(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 4), send(230, 8), close(250))

        def create():
            return xs.contains(21, lambda a, b: a % 2 == b % 2)

        res = scheduler.start(create=create).messages
        assert res == [send(250, False), close(250)]
