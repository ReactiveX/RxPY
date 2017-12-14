import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestMin(unittest.TestCase):
    def test_min_int32_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(250))

        def create():
            return xs.min()
        res = scheduler.start(create=create).messages
        assert(1 == len(res))
        assert(res[0].value.kind == 'E' and res[0].value.exception)
        assert(res[0].time == 250)

    def test_min_int32_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), close(250))
        res = scheduler.start(create=lambda: xs.min()).messages
        assert res == [send(250, 2), close(250)]

    def test_min_int32_some(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), close(250))
        res = scheduler.start(create=lambda: xs.min()).messages
        assert res == [send(250, 2), close(250)]

    def test_min_int32_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(210, ex))
        res = scheduler.start(create=lambda: xs.min()).messages
        assert res == [throw(210, ex)]

    def test_min_int32_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1))
        res = scheduler.start(create=lambda: xs.min()).messages
        assert res == []

    def test_min_of_t_comparer_empty(self):
        scheduler = TestScheduler()
        def comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0

            return 1

        xs = scheduler.create_hot_observable(send(150, 'a'), close(250))

        def create():
            return xs.min(comparer)

        res = scheduler.start(create=create).messages
        self.assertEqual(1, len(res))
        assert(res[0].value.kind == 'E' and res[0].value.exception != None)
        assert(res[0].time == 250)

    def test_min_of_t_comparer_empty_ii(self):
        scheduler = TestScheduler()
        def comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0

            return 1

        xs = scheduler.create_hot_observable(send(150, 'z'), send(210, "b"), send(220, "c"), send(230, "a"), close(250))

        def create():
            return xs.min(comparer)

        res = scheduler.start(create=create).messages
        assert res == [send(250, "c"), close(250)]

    def test_min_of_t_comparer_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        def comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0

            return 1

        xs = scheduler.create_hot_observable(send(150, 'z'), throw(210, ex))

        def create():
            return xs.min(comparer)

        res = scheduler.start(create=create).messages
        assert res == [throw(210, ex)]

    def test_min_of_t_comparer_never(self):
        scheduler = TestScheduler()
        def comparer(a, b):
            if a > b:
                return -1

            if a == b:
                return 0

            return 1

        xs = scheduler.create_hot_observable(send(150, 'z'))

        def create():
            return xs.min(comparer)
        res = scheduler.start(create=create).messages
        assert res == []

    def test_min_of_t_comparer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        def comparer(a, b):
            raise Exception(ex)

        xs = scheduler.create_hot_observable(send(150, 'z'), send(210, "b"), send(220, "c"), send(230, "a"), close(250))

        def create():
            return xs.min(comparer)

        res = scheduler.start(create=create).messages
        assert res == [throw(220, ex)]
