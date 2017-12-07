import unittest
from datetime import datetime

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime
from rx.disposables import SerialDisposable

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


def test_is_prime():
    assert is_prime(1) == False
    assert is_prime(2) == True
    assert is_prime(3) == True
    assert is_prime(4) == False
    assert is_prime(5) == True
    assert is_prime(6) == False


class TestFilter(unittest.TestCase):
    def test_filter_complete(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1),
                                             send(180, 2), send(230, 3),
                                             send(270, 4), send(340, 5),
                                             send(380, 6), send(390, 7),
                                             send(450, 8), send(470, 9),
                                             send(560, 10), send(580, 11),
                                             close(600), send(610, 12),
                                             throw(620, 'ex'), close(630))

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)

            return xs.filter(predicate)

        results = scheduler.start(create)

        results.messages.assert_equal(send(230, 3),
                                      send(340, 5), send(390, 7),
                                      send(580, 11), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        assert invoked[0] == 9

    def test_filter_true(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600))

        def create():
            def predicate(x):
                invoked[0] += 1
                return True
            return xs.filter(predicate)

        results = scheduler.start(create)
        results.messages.assert_equal(send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        assert invoked[0] == 9

    def test_filter_false(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600))

        def create():
            def predicate(x):
                invoked[0] += 1
                return False

            return xs.filter(predicate)

        results = scheduler.start(create)

        results.messages.assert_equal(close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        assert invoked[0] == 9

    def test_filter_dispose(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600))

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.filter(predicate)

        results = scheduler.start(create, disposed=400)
        results.messages.assert_equal(send(230, 3), send(340, 5), send(390, 7))
        xs.subscriptions.assert_equal(subscribe(200, 400))
        assert(invoked[0] == 5)

    def test_filter_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), throw(600, ex), send(610, 12), throw(620, 'ex'), close(630))

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.filter(predicate)

        results = scheduler.start(create)

        results.messages.assert_equal(send(230, 3), send(340, 5), send(390, 7), send(580, 11), throw(600, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        assert(invoked[0] == 9)

    def test_filter_throw(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600), send(610, 12), throw(620, 'ex'), close(630))

        def create():
            def predicate(x):
                invoked[0] += 1
                if x > 5:
                    raise Exception(ex)

                return is_prime(x)
            return xs.filter(predicate)

        results = scheduler.start(create)

        results.messages.assert_equal(send(230, 3), send(340, 5), throw(380, ex))
        xs.subscriptions.assert_equal(subscribe(200, 380))
        assert(invoked[0] == 4)

    def test_filter_dispose_in_predicate(self):
        scheduler = TestScheduler()
        invoked = [0]
        ys = [None]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600), send(610, 12), throw(620, 'ex'), close(630))
        results = scheduler.create_observer()
        d = SerialDisposable()

        def action(scheduler, state):

            def predicate(x):
                invoked[0] += 1
                if x == 8:
                    d.dispose()

                return is_prime(x)
            ys[0] = xs.filter(predicate)
            return ys[0]

        scheduler.schedule_absolute(created, action)

        def action1(scheduler, state):
            d.disposable = ys[0].subscribe(results)

        scheduler.schedule_absolute(subscribed, action1)

        def action2(scheduler, state):
            d.dispose()

        scheduler.schedule_absolute(disposed, action2)

        scheduler.start()
        results.messages.assert_equal(send(230, 3), send(340, 5), send(390, 7))
        xs.subscriptions.assert_equal(subscribe(200, 450))
        assert(invoked[0] == 6)

    def test_filter_indexed_complete(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600), send(610, 12), throw(620, 'ex'), close(630))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return is_prime(x + index * 10)

            return xs.filter_indexed(predicate)

        results = scheduler.start(create)
        results.messages.assert_equal(send(230, 3), send(390, 7), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        assert(invoked[0] == 9)

    def test_filter_indexed_true(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return True

            return xs.filter_indexed(predicate)

        results = scheduler.start(create)
        results.messages.assert_equal(send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        assert(invoked[0] == 9)

    def test_filter_indexed_false(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return False
            return xs.filter_indexed(predicate)

        results = scheduler.start(create)

        results.messages.assert_equal(close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        assert(invoked[0] == 9)

    def test_filter_indexed_dispose(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return is_prime(x + index * 10)

            return xs.filter_indexed(predicate)

        results = scheduler.start(create, disposed=400)
        results.messages.assert_equal(send(230, 3), send(390, 7))
        xs.subscriptions.assert_equal(subscribe(200, 400))
        assert(invoked[0] == 5)

    def test_filter_indexed_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), throw(600, ex), send(610, 12), throw(620, 'ex'), close(630))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return is_prime(x + index * 10)
            return xs.filter_indexed(predicate)

        results = scheduler.start(create)

        results.messages.assert_equal(send(230, 3), send(390, 7), throw(600, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))
        assert(invoked[0] == 9)

    def test_filter_indexed_throw(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600), send(610, 12), throw(620, 'ex'), close(630))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                if x > 5:
                    raise Exception(ex)

                return is_prime(x + index * 10)
            return xs.filter_indexed(predicate)

        results = scheduler.start(create)
        results.messages.assert_equal(send(230, 3), throw(380, ex))
        xs.subscriptions.assert_equal(subscribe(200, 380))
        assert(invoked[0] == 4)

    def test_filter_indexed_dispose_in_predicate(self):
        scheduler = TestScheduler()
        ys = [None]
        invoked = [0]
        xs = scheduler.create_hot_observable(send(110, 1), send(180, 2), send(230, 3), send(270, 4), send(340, 5), send(380, 6), send(390, 7), send(450, 8), send(470, 9), send(560, 10), send(580, 11), close(600), send(610, 12), throw(620, 'ex'), close(630))
        results = scheduler.create_observer()
        d = SerialDisposable()

        def action1(scheduler, state):
            def predicate(x, index):
                invoked[0] += 1
                if x == 8:
                    d.dispose()

                return is_prime(x + index * 10)
            ys[0] = xs.filter_indexed(predicate)

        scheduler.schedule_absolute(created, action1)

        def action2(scheduler, state):
             d.disposable = ys[0].subscribe(results)

        scheduler.schedule_absolute(subscribed, action2)

        def action3(scheduler, state):
            d.dispose()

        scheduler.schedule_absolute(disposed, action3)

        scheduler.start()
        results.messages.assert_equal(send(230, 3), send(390, 7))
        xs.subscriptions.assert_equal(subscribe(200, 450))
        assert(invoked[0] == 6)
