import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestFirst(unittest.TestCase):
    def test_first_async_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(250))
        def create():
            return xs.first()

        res = scheduler.start(create=create)

        assert [throw(250, lambda e: e)] == res.messages
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_first_async_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), close(250))
        res = scheduler.start(lambda: xs.first())

        assert res.messages == [send(210, 2), close(210)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_first_async_many(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), close(250))
        res = scheduler.start(lambda: xs.first())

        assert res.messages == [send(210, 2), close(210)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_first_async_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(210, ex))
        res = scheduler.start(lambda: xs.first())

        assert res.messages == [throw(210, ex)]
        assert xs.subscriptions == [subscribe(200, 210)]

    def test_first_async_predicate(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250))

        def create():
            return xs.first(lambda x: x % 2 == 1)
        res = scheduler.start(create=create)

        assert res.messages == [send(220, 3), close(220)]
        assert xs.subscriptions == [subscribe(200, 220)]

    def test_first_async_predicate_none(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250))

        def create():
            return xs.first(lambda x: x > 10)

        res = scheduler.start(create=create)

        assert [throw(250, lambda e: e)] == res.messages
        assert xs.subscriptions == [subscribe(200, 250)]


    def test_first_async_predicate_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), throw(220, ex))

        def create():
            return xs.first(lambda x: x % 2 == 1)

        res = scheduler.start(create=create)

        assert res.messages == [throw(220, ex)]
        assert xs.subscriptions == [subscribe(200, 220)]

    def test_first_async_predicate_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250))

        def create():
            def predicate(x):
                if x < 4:
                    return False
                else:
                    raise Exception(ex)

            return xs.first(predicate)

        res = scheduler.start(create=create)

        assert res.messages == [throw(230, ex)]
        assert xs.subscriptions == [subscribe(200, 230)]

if __name__ == '__main__':
    unittest.main()
