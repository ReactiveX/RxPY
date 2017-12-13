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

class TestSkipWhile(unittest.TestCase):
    def test_skip_while_complete_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), close(330), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.skip_while(predicate)
        results = scheduler.start(create)

        assert results.messages == [close(330)]
        assert xs.subscriptions == [subscribe(200, 330)]
        assert(invoked[0] == 4)

    def test_skip_while_complete_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.skip_while(predicate)
        results = scheduler.start(create)

        assert results.messages == [send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 6)

    def test_skip_while_error_before(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), throw(270, ex), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.skip_while(predicate)
        results = scheduler.start(create)

        assert results.messages == [throw(270, ex)]
        assert xs.subscriptions == [subscribe(200, 270)]
        assert(invoked[0] == 2)

    def test_skip_while_error_after(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), throw(600, ex))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.skip_while(predicate)
        results = scheduler.start(create)

        assert results.messages == [send(390, 4), send(410, 17), send(450, 8), send(500, 23), throw(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 6)

    def test_skip_while_dispose_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.skip_while(predicate)
        results = scheduler.start(create, disposed=300)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 300)]
        assert(invoked[0] == 3)

    def test_skip_while_dispose_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.skip_while(predicate)
        results = scheduler.start(create, disposed=470)

        assert results.messages == [send(390, 4), send(410, 17), send(450, 8)]
        assert xs.subscriptions == [subscribe(200, 470)]
        assert(invoked[0] == 6)

    def test_skip_while_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(205, 100), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.skip_while(predicate)
        results = scheduler.start(create)

        assert results.messages == [send(205, 100), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 1)

    def test_skip_while_throw(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))
        ex = 'ex'
        invoked = [0]
        def create():
            def predicate(x):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)

                return is_prime(x)
            return xs.skip_while(predicate)
        results = scheduler.start(create)

        assert results.messages == [throw(290, ex)]
        assert xs.subscriptions == [subscribe(200, 290)]
        assert(invoked[0] == 3)

    def test_skip_while_index(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(90, -1), send(110, -1), send(210, 2), send(260, 5), send(290, 13), send(320, 3), send(350, 7), send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600))

        def create():
            def predicate(x, i):
                return i < 5
            return xs.skip_while(predicate)
        results = scheduler.start(create)

        assert results.messages == [send(390, 4), send(410, 17), send(450, 8), send(500, 23), close(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
