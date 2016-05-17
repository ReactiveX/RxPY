import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestDoWhile(unittest.TestCase):

    def test_dowhile_always_false(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))

        def create():
            return xs.do_while(lambda _: False)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_completed(450))
        xs.subscriptions.assert_equal(subscribe(200, 450))

    def test_dowhile_always_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_next(750, 1), on_next(800, 2), on_next(850, 3), on_next(900, 4))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1000))

    def test_dowhile_always_true_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_error(50, ex))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_error(250, ex))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_dowhile_always_true_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(250, 1))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_dowhile_sometimes_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
        n = [0]

        def create():
            def condition(x):
                n[0] += 1
                return n[0]<3
            return xs.do_while(condition)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_next(750, 1), on_next(800, 2), on_next(850, 3), on_next(900, 4), on_completed(950))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950))

    def test_dowhile_sometimes_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
        n = [0]

        def create():
            def condition(x):
                n[0] += 1
                if n[0]<3:
                    return True
                else:
                    raise Exception(ex)
            return xs.do_while(condition)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_next(750, 1), on_next(800, 2), on_next(850, 3), on_next(900, 4), on_error(950, ex))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950))
