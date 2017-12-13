import unittest

from rx.testing import TestScheduler, ReactiveTest


class TestDoWhile(ReactiveTest, unittest.TestCase):

    def test_dowhile_always_false(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
            self.send(50, 1),
            self.send(100, 2),
            self.send(150, 3),
            self.send(200, 4),
            self.close(250))

        def create():
            return xs.do_while(lambda _: False)
        results = scheduler.start(create=create)

        assert results.messages == [
            self.send(250, 1),
            self.send(300, 2),
            self.send(350, 3),
            self.send(400, 4),
            self.close(450)]
        assert xs.subscriptions == [self.subscribe(200, 450)]

    def test_dowhile_always_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
            self.send(50, 1),
            self.send(100, 2),
            self.send(150, 3),
            self.send(200, 4),
            self.close(250))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        assert results.messages == [
            self.send(250, 1),
            self.send(300, 2),
            self.send(350, 3),
            self.send(400, 4),
            self.send(500, 1),
            self.send(550, 2),
            self.send(600, 3),
            self.send(650, 4),
            self.send(750, 1),
            self.send(800, 2),
            self.send(850, 3),
            self.send(900, 4)]
        assert xs.subscriptions == [
            self.subscribe(200, 450),
            self.subscribe(450, 700),
            self.subscribe(700, 950),
            self.subscribe(950, 1000)]

    def test_dowhile_always_true_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(self.throw(50, ex))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        assert results.messages == [self.throw(250, ex)]
        assert xs.subscriptions == [self.subscribe(200, 250)]

    def test_dowhile_always_true_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(self.send(50, 1))

        def create():
            return xs.do_while(lambda _: True)
        results = scheduler.start(create=create)

        assert results.messages == [
            self.send(250, 1)]
        assert xs.subscriptions == [self.subscribe(200, 1000)]

    def test_dowhile_sometimes_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
            self.send(50, 1),
            self.send(100, 2),
            self.send(150, 3),
            self.send(200, 4),
            self.close(250))
        n = [0]

        def create():
            def condition(x):
                n[0] += 1
                return n[0]<3
            return xs.do_while(condition)
        results = scheduler.start(create=create)

        assert results.messages == [
            self.send(250, 1),
            self.send(300, 2),
            self.send(350, 3),
            self.send(400, 4),
            self.send(500, 1),
            self.send(550, 2),
            self.send(600, 3),
            self.send(650, 4),
            self.send(750, 1),
            self.send(800, 2),
            self.send(850, 3),
            self.send(900, 4),
            self.close(950)]
        assert xs.subscriptions == [
            self.subscribe(200, 450),
            self.subscribe(450, 700),
            self.subscribe(700, 950)]

    def test_dowhile_sometimes_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
            self.send(50, 1),
            self.send(100, 2),
            self.send(150, 3),
            self.send(200, 4),
            self.close(250))
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

        assert results.messages == [
            self.send(250, 1),
            self.send(300, 2),
            self.send(350, 3),
            self.send(400, 4),
            self.send(500, 1),
            self.send(550, 2),
            self.send(600, 3),
            self.send(650, 4),
            self.send(750, 1),
            self.send(800, 2),
            self.send(850, 3),
            self.send(900, 4),
            self.throw(950, ex)]
        assert xs.subscriptions == [
            self.subscribe(200, 450),
            self.subscribe(450, 700),
            self.subscribe(700, 950)]
