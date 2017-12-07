import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestDoWhile(unittest.TestCase):

    def test_dowhile_always_false(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(50, 1), send(100, 2), send(150, 3), send(200, 4), close(250))

        def create():
            return xs.do_while(lambda _: False)
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(250, 1), send(300, 2), send(350, 3), send(400, 4), close(450))
        xs.subscriptions.assert_equal(subscribe(200, 450))

    def test_dowhile_always_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(50, 1), send(100, 2), send(150, 3), send(200, 4), close(250))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(250, 1), send(300, 2), send(350, 3), send(400, 4), send(500, 1), send(550, 2), send(600, 3), send(650, 4), send(750, 1), send(800, 2), send(850, 3), send(900, 4))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1000))

    def test_dowhile_always_true_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(throw(50, ex))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        results.messages.assert_equal(throw(250, ex))
        xs.subscriptions.assert_equal(subscribe(200, 250))

    def test_dowhile_always_true_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(50, 1))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(250, 1))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_dowhile_sometimes_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(50, 1), send(100, 2), send(150, 3), send(200, 4), close(250))
        n = [0]

        def create():
            def condition(x):
                n[0] += 1
                return n[0]<3
            return xs.do_while(condition)
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(250, 1), send(300, 2), send(350, 3), send(400, 4), send(500, 1), send(550, 2), send(600, 3), send(650, 4), send(750, 1), send(800, 2), send(850, 3), send(900, 4), close(950))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950))

    def test_dowhile_sometimes_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(50, 1), send(100, 2), send(150, 3), send(200, 4), close(250))
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

        results.messages.assert_equal(send(250, 1), send(300, 2), send(350, 3), send(400, 4), send(500, 1), send(550, 2), send(600, 3), send(650, 4), send(750, 1), send(800, 2), send(850, 3), send(900, 4), throw(950, ex))
        xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950))
