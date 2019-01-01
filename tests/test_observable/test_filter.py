import unittest

from rx.testing import TestScheduler, ReactiveTest, is_prime
from rx.disposables import SerialDisposable

from rx.operators.filter import filter, filteri

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
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
    assert not is_prime(1)
    assert is_prime(2)
    assert is_prime(3)
    assert not is_prime(4)
    assert is_prime(5)
    assert not is_prime(6)


class TestFilter(unittest.TestCase):
    def test_filter_complete(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1),
                                             on_next(180, 2), on_next(230, 3),
                                             on_next(270, 4), on_next(340, 5),
                                             on_next(380, 6), on_next(390, 7),
                                             on_next(450, 8), on_next(470, 9),
                                             on_next(560, 10), on_next(
                                                 580, 11),
                                             on_completed(
                                                 600), on_next(610, 12),
                                             on_error(620, 'ex'), on_completed(630))

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)

            return xs.pipe(filter(predicate))

        results = scheduler.start(create)

        assert results.messages == [on_next(230, 3),
                                    on_next(340, 5), on_next(390, 7),
                                    on_next(580, 11), on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert invoked[0] == 9

    def test_filter_true(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(
            380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))

        def create():
            def predicate(x):
                invoked[0] += 1
                return True
            return xs.pipe(filter(predicate))

        results = scheduler.start(create)
        assert results.messages == [on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(
            390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert invoked[0] == 9

    def test_filter_false(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(
            380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))

        def create():
            def predicate(x):
                invoked[0] += 1
                return False

            return xs.pipe(filter(predicate))

        results = scheduler.start(create)

        assert results.messages == [on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert invoked[0] == 9

    def test_filter_dispose(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(
            380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(filter(predicate))

        results = scheduler.start(create, disposed=400)
        assert results.messages == [
            on_next(230, 3), on_next(340, 5), on_next(390, 7)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert(invoked[0] == 5)

    def test_filter_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            on_next(110, 1),
            on_next(180, 2),
            on_next(230, 3),
            on_next(270, 4),
            on_next(340, 5),
            on_next(380, 6),
            on_next(390, 7),
            on_next(450, 8),
            on_next(470, 9),
            on_next(560, 10),
            on_next(580, 11),
            on_error(600, ex),
            on_next(610, 12),
            on_error(620, 'ex'),
            on_completed(630))

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(filter(predicate))

        results = scheduler.start(create)

        assert results.messages == [on_next(230, 3), on_next(
            340, 5), on_next(390, 7), on_next(580, 11), on_error(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 9)

    def test_filter_on_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(
            390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))

        def create():
            def predicate(x):
                invoked[0] += 1
                if x > 5:
                    raise Exception(ex)

                return is_prime(x)
            return xs.pipe(filter(predicate))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(230, 3), on_next(340, 5), on_error(380, ex)]
        assert xs.subscriptions == [subscribe(200, 380)]
        assert(invoked[0] == 4)

    def test_filter_dispose_in_predicate(self):
        scheduler = TestScheduler()
        invoked = [0]
        ys = [None]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(
            390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
        results = scheduler.create_observer()
        d = SerialDisposable()

        def action(scheduler, state):

            def predicate(x):
                invoked[0] += 1
                if x == 8:
                    d.dispose()

                return is_prime(x)
            ys[0] = xs.pipe(filter(predicate))
            return ys[0]

        scheduler.schedule_absolute(created, action)

        def action1(scheduler, state):
            d.disposable = ys[0].subscribe(results)

        scheduler.schedule_absolute(subscribed, action1)

        def action2(scheduler, state):
            d.dispose()

        scheduler.schedule_absolute(disposed, action2)

        scheduler.start()
        assert results.messages == [
            on_next(230, 3), on_next(340, 5), on_next(390, 7)]
        assert xs.subscriptions == [subscribe(200, 450)]
        assert(invoked[0] == 6)

    def test_filter_indexed_complete(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(
            390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return is_prime(x + index * 10)

            return xs.pipe(filteri(predicate))

        results = scheduler.start(create)
        assert results.messages == [
            on_next(230, 3), on_next(390, 7), on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 9)

    def test_filter_indexed_true(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(
            380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return True

            return xs.pipe(filteri(predicate))

        results = scheduler.start(create)
        assert results.messages == [on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(
            390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 9)

    def test_filter_indexed_false(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(
            380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return False
            return xs.pipe(filteri(predicate))

        results = scheduler.start(create)

        assert results.messages == [on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 9)

    def test_filter_indexed_dispose(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(
            380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return is_prime(x + index * 10)

            return xs.pipe(filteri(predicate))

        results = scheduler.start(create, disposed=400)
        assert results.messages == [on_next(230, 3), on_next(390, 7)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert(invoked[0] == 5)

    def test_filter_indexed_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(
            390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_error(600, ex), on_next(610, 12), on_error(620, 'ex'), on_completed(630))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                return is_prime(x + index * 10)
            return xs.pipe(filteri(predicate))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(230, 3), on_next(390, 7), on_error(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 9)

    def test_filter_indexed_on_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(
            390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))

        def create():
            def predicate(x, index):
                invoked[0] += 1
                if x > 5:
                    raise Exception(ex)

                return is_prime(x + index * 10)
            return xs.pipe(filteri(predicate))

        results = scheduler.start(create)
        assert results.messages == [on_next(230, 3), on_error(380, ex)]
        assert xs.subscriptions == [subscribe(200, 380)]
        assert(invoked[0] == 4)

    def test_filter_indexed_dispose_in_predicate(self):
        scheduler = TestScheduler()
        ys = [None]
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(
            390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
        results = scheduler.create_observer()
        d = SerialDisposable()

        def action1(scheduler, state):
            def predicate(x, index):
                invoked[0] += 1
                if x == 8:
                    d.dispose()

                return is_prime(x + index * 10)
            ys[0] = xs.pipe(filteri(predicate))

        scheduler.schedule_absolute(created, action1)

        def action2(scheduler, state):
            d.disposable = ys[0].subscribe(results)

        scheduler.schedule_absolute(subscribed, action2)

        def action3(scheduler, state):
            d.dispose()

        scheduler.schedule_absolute(disposed, action3)

        scheduler.start()
        assert results.messages == [on_next(230, 3), on_next(390, 7)]
        assert xs.subscriptions == [subscribe(200, 450)]
        assert(invoked[0] == 6)
