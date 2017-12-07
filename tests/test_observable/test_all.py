import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestAll(unittest.TestCase):

    def test_all_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.all(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, True), close(250))

    def test_all_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.all(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, True), close(250))

    def test_all_return_not_match(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, -2), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.all(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(210, False), close(210))

    def test_all_some_none_match(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, -2), send(220, -3), send(230, -4), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.all(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(210, False), close(210))

    def test_all_some_match(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, -2), send(220, 3), send(230, -4), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.all(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(210, False), close(210))

    def test_all_some_all_match(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(210, 2), send(220, 3), send(230, 4), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.all(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal(send(250, True), close(250))

    def test_all_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(210, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.all(lambda x: x > 0)
        res = scheduler.start(create=create).messages
        res.assert_equal(throw(210, ex))

    def test_all_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.all(lambda x: x > 0)

        res = scheduler.start(create=create).messages
        res.assert_equal()

if __name__ == '__main__':
    unittest.main()
