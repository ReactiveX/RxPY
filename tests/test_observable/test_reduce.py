import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestReduce(unittest.TestCase):

    def test_reduce_with_seed_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(lambda acc, x: acc + x, 42)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, 42), close(250))

    def test_reduce_with_seed_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 24), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(accumulator=lambda acc, x: acc + x, seed=42)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, 42 + 24), close(250))

    def test_reduce_with_seed_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(accumulator=lambda acc, x: acc + x, seed=42)

        res = scheduler.start(create=create).messages
        res.assert_equal(throw(210, ex))

    def test_reduce_with_seed_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(accumulator=lambda acc, x: acc + x, seed=42)

        res = scheduler.start(create=create).messages
        res.assert_equal()

    def test_reduce_with_seed_range(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 0), send(220, 1), send(230, 2), send(240, 3), send(250, 4), close(260)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(accumulator=lambda acc, x: acc + x, seed=42)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(260, 10 + 42), close(260))

    def test_reduce_without_seed_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(accumulator=lambda acc, x: acc + x)

        res = scheduler.start(create=create).messages
        assert(len(res) == 1)
        assert(res[0].value.kind == 'E' and res[0].value.exception != None)
        assert(res[0].time == 250)

    def test_reduce_without_seed_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 24), close(250)]

        def create():
            return xs.reduce(accumulator=lambda acc, x: acc + x)

        xs = scheduler.create_hot_observable(msgs)
        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, 24), close(250))

    def test_reduce_without_seed_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(lambda acc, x: acc + x)

        res = scheduler.start(create=create).messages
        res.assert_equal(throw(210, ex))

    def test_reduce_without_seed_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(lambda acc, x: acc + x)

        res = scheduler.start(create=create).messages
        res.assert_equal()

    def test_reduce_without_seed_range(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 0), send(220, 1), send(230, 2), send(240, 3), send(250, 4), close(260)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.reduce(lambda acc, x: acc + x)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(260, 10), close(260))

if __name__ == '__main__':
    unittest.main()

