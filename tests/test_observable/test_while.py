import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestWhile(unittest.TestCase):
    def test_while_always_false(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))

        def create():
            return Observable.while_do(lambda _: False, xs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(200))
        xs.subscriptions.assert_equal()

    def test_while_always_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))

        def create():
            return Observable.while_do(lambda _: True, xs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_next(750, 1), on_next(800, 2), on_next(850, 3), on_next(900, 4))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1000))

    def test_while_always_true_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_error(50, ex))
        def create():
            return Observable.while_do(lambda _: True, xs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(250, ex))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_while_always_true_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1))
        def create():
            return Observable.while_do(lambda _: True, xs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(250, 1))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_dowhile_always_true_infinite_with_create(self):
        scheduler = TestScheduler()
        n = [0]

        def create():
            import sys
            sys.setrecursionlimit(1000)
            def predicate(x):
                n[0] += 1
                return n[0] < 1000
            def subscribe(o):
                o.on_next(1)
                o.on_completed()
                return lambda: None
            return Observable.while_do(predicate, Observable.create(subscribe))
        results = scheduler.start(create=create)

        results.messages.assert_equal(*([on_next(200, 1) for _ in range(999)] + [on_completed(200)]))

    def test_while_sometimes_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
        n = [0]

        def create():
            def predicate(x):
                n[0] += 1
                return n[0] < 3
            return Observable.while_do(predicate, xs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_completed(700))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700))

    def test_while_sometimes_throws(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
        n = [0]
        ex = 'ex'

        def create():
            def predicate(x):
                n[0] += 1
                if n[0] < 3:
                    return True
                else:
                    raise Exception(ex)

            return Observable.while_do(predicate, xs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_error(700, ex))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700))
