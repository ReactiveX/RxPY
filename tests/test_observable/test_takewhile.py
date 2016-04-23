import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestTakeWhile(unittest.TestCase):

    def test_take_while_complete_Before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_completed(330), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_completed(330))
        xs.subscriptions.assert_equal(subscribe(200, 330))
        assert(invoked[0] == 4)

    def test_take_while_complete_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_completed(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
        assert(invoked[0] == 6)

    def test_take_while_error_before(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(210, 2), on_next(260, 5), on_error(270, ex), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(210, 2), on_next(260, 5), on_error(270, ex))
        xs.subscriptions.assert_equal(subscribe(200, 270))
        assert(invoked[0] == 2)

    def test_take_while_error_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23), on_error(600, 'ex'))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_completed(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
        assert(invoked[0] == 6)

    def test_take_while_dispose_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(create, disposed=300)
        results.messages.assert_equal(on_next(210, 2), on_next(260, 5), on_next(290, 13))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        assert(invoked[0] == 3)

    def test_take_while_dispose_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(create, disposed=400)
        results.messages.assert_equal(on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_completed(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
        assert(invoked[0] == 6)

    def test_take_while_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(205, 100), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(create, disposed=300)
        results.messages.assert_equal(on_completed(205))
        xs.subscriptions.assert_equal(subscribe(200, 205))
        assert (invoked[0] == 1)

    def test_take_while_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)

                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(210, 2), on_next(260, 5), on_error(290, ex))
        xs.subscriptions.assert_equal(subscribe(200, 290))
        assert(invoked[0] == 3)

    def test_take_while_index(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, -1), on_next(110, -1), on_next(205, 100), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_next(350, 7), on_next(390, 4), on_next(410, 17), on_next(450, 8), on_next(500, 23), on_completed(600))

        def factory():
            return xs.take_while(lambda x, i: i < 5)
        results = scheduler.start(factory)

        results.messages.assert_equal(on_next(205, 100), on_next(210, 2), on_next(260, 5), on_next(290, 13), on_next(320, 3), on_completed(350))
        xs.subscriptions.assert_equal(subscribe(200, 350))
