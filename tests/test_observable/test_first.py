import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestFirst(unittest.TestCase):
    def test_first_async_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
        def create():
            return xs.first()

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(250, lambda e: e))

        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_first_async_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
        res = scheduler.start(lambda: xs.first())

        res.messages.assert_equal(on_next(210, 2), on_completed(210))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_first_async_many(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
        res = scheduler.start(lambda: xs.first())

        res.messages.assert_equal(on_next(210, 2), on_completed(210))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_first_async_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
        res = scheduler.start(lambda: xs.first())

        res.messages.assert_equal(on_error(210, ex))
        xs.subscriptions.assert_equal(subscribe(200, 210))

    def test_first_async_predicate(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

        def create():
            return xs.first(lambda x: x % 2 == 1)
        res = scheduler.start(create=create)

        res.messages.assert_equal(on_next(220, 3), on_completed(220))
        xs.subscriptions.assert_equal(subscribe(200, 220))

    def test_first_async_predicate_none(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

        def create():
            return xs.first(lambda x: x > 10)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(250, lambda e: e))
        xs.subscriptions.assert_equal(subscribe(200, 250))


    def test_first_async_predicate_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_error(220, ex))

        def create():
            return xs.first(lambda x: x % 2 == 1)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(220, ex))
        xs.subscriptions.assert_equal(subscribe(200, 220))

    def test_first_async_predicate_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

        def create():
            def predicate(x):
                if x < 4:
                    return False
                else:
                    raise Exception(ex)

            return xs.first(predicate)

        res = scheduler.start(create=create)

        res.messages.assert_equal(on_error(230, ex))
        xs.subscriptions.assert_equal(subscribe(200, 230))

if __name__ == '__main__':
    unittest.main()
