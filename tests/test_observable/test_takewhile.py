import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestTakeWhile(unittest.TestCase):

    def test_take_while_complete_Before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), close(330), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(send(210, 2), send(260, 5), send(290, 13), send(320, 3), close(330))
        xs.subscriptions.assert_equal(subscribe(200, 330))
        assert(invoked[0] == 4)

    def test_take_while_complete_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), close(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
        assert(invoked[0] == 6)

    def test_take_while_error_before(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), throw(270, ex), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(send(210, 2), send(260, 5), throw(270, ex))
        xs.subscriptions.assert_equal(subscribe(200, 270))
        assert(invoked[0] == 2)

    def test_take_while_error_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), throw(600, 'ex'))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), close(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
        assert(invoked[0] == 6)

    def test_take_while_dispose_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(create, disposed=300)
        results.messages.assert_equal(send(210, 2), send(260, 5), send(290, 13))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        assert(invoked[0] == 3)

    def test_take_while_dispose_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(create, disposed=400)
        results.messages.assert_equal(send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), close(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
        assert(invoked[0] == 6)

    def test_take_while_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(205, 100), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(create, disposed=300)
        results.messages.assert_equal(close(205))
        xs.subscriptions.assert_equal(subscribe(200, 205))
        assert (invoked[0] == 1)

    def test_take_while_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def factory():
            def predicate(x):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)

                return is_prime(x)
            return xs.take_while(predicate)
        results = scheduler.start(factory)

        results.messages.assert_equal(send(210, 2), send(260, 5), throw(290, ex))
        xs.subscriptions.assert_equal(subscribe(200, 290))
        assert(invoked[0] == 3)

    def test_take_while_index(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(205, 100), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))

        def factory():
            return xs.take_while(lambda x, i: i < 5)
        results = scheduler.start(factory)

        results.messages.assert_equal(send(205, 100), send(210, 2), send(260, 5), send(290, 13), send(320, 3), close(350))
        xs.subscriptions.assert_equal(subscribe(200, 350))
