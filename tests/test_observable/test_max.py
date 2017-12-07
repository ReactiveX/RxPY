import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestMax(unittest.TestCase):
    def test_max_int32_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.max()

        res = scheduler.start(create=create).messages
        self.assertEqual(1, len(res))
        assert(res[0].value.kind == 'E' and res[0].value.exception != None)
        assert(res[0].time == 250)

    def test_max_int32_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max()

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, 2), close(250))

    def test_max_int32_some(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 3), send(220, 4), send(230, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max()

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, 4), close(250))

    def test_max_int32_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(210, ex)]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.max()
        res = scheduler.start(create=create).messages
        res.assert_equal(throw(210, ex))

    def test_max_int32_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1)]
        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.max()

        res = scheduler.start(create=create).messages
        res.assert_equal()

    def test_max_of_t_comparer_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a < b:
                return 1

            return 0

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max(reverse_comparer)

        res = scheduler.start(create=create).messages
        self.assertEqual(1, len(res))
        assert(res[0].value.kind == 'E' and res[0].value.exception != None)
        assert(res[0].time == 250)

    def test_max_of_t_comparer_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 'z'), send(210, 'a'), close(250)]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a < b:
                return 1

            return 0

        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.max(reverse_comparer)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, 'a'), close(250))

    def test_max_of_t_comparer_some(self):
        scheduler = TestScheduler()
        msgs = [send(150, 'z'), send(210, 'b'), send(220, 'c'), send(230, 'a'), close(250)]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a < b:
                return 1

            return 0

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max(reverse_comparer)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, 'a'), close(250))

    def test_max_of_t_comparer_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 'z'), throw(210, ex)]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a < b:
                return 1

            return 0

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max(reverse_comparer)

        res = scheduler.start(create=create).messages
        res.assert_equal(throw(210, ex))

    def test_max_of_t_comparer_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 'z')]
        def reverse_comparer(a, b):
            if a > b:
                return -1

            if a < b:
                return 1

            return 0

        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.max(reverse_comparer)

        res = scheduler.start(create=create).messages
        res.assert_equal()

    def test_max_of_t_comparer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 'z'), send(210, 'b'), send(220, 'c'), send(230, 'a'), close(250)]
        def reverse_comparer(a, b):
            raise Exception(ex)

        xs = scheduler.create_hot_observable(msgs)
        def create():
            return xs.max(reverse_comparer)
        res = scheduler.start(create=create).messages

        res.assert_equal(throw(220, ex))
