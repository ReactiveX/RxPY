import unittest

from reactivex import operators as ops
from reactivex.testing import ReactiveTest, TestScheduler


class TestDoWhile(ReactiveTest, unittest.TestCase):
    def test_dowhile_always_false(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
            self.on_next(50, 1),
            self.on_next(100, 2),
            self.on_next(150, 3),
            self.on_next(200, 4),
            self.on_completed(250),
        )

        def create():
            return xs.pipe(ops.do_while(lambda _: False))

        results = scheduler.start(create=create)

        assert results.messages == [
            self.on_next(250, 1),
            self.on_next(300, 2),
            self.on_next(350, 3),
            self.on_next(400, 4),
            self.on_completed(450),
        ]
        assert xs.subscriptions == [self.subscribe(200, 450)]

    def test_dowhile_always_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
            self.on_next(50, 1),
            self.on_next(100, 2),
            self.on_next(150, 3),
            self.on_next(200, 4),
            self.on_completed(250),
        )

        def create():
            return xs.pipe(ops.do_while(lambda _: True))

        results = scheduler.start(create=create)

        assert results.messages == [
            self.on_next(250, 1),
            self.on_next(300, 2),
            self.on_next(350, 3),
            self.on_next(400, 4),
            self.on_next(500, 1),
            self.on_next(550, 2),
            self.on_next(600, 3),
            self.on_next(650, 4),
            self.on_next(750, 1),
            self.on_next(800, 2),
            self.on_next(850, 3),
            self.on_next(900, 4),
        ]
        assert xs.subscriptions == [
            self.subscribe(200, 450),
            self.subscribe(450, 700),
            self.subscribe(700, 950),
            self.subscribe(950, 1000),
        ]

    def test_dowhile_always_true_on_error(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(self.on_error(50, ex))

        def create():
            return xs.pipe(ops.do_while(lambda _: True))

        results = scheduler.start(create=create)

        assert results.messages == [self.on_error(250, ex)]
        assert xs.subscriptions == [self.subscribe(200, 250)]

    def test_dowhile_always_true_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(self.on_next(50, 1))

        def create():
            return xs.pipe(ops.do_while(lambda _: True))

        results = scheduler.start(create=create)

        assert results.messages == [self.on_next(250, 1)]
        assert xs.subscriptions == [self.subscribe(200, 1000)]

    def test_dowhile_sometimes_true(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
            self.on_next(50, 1),
            self.on_next(100, 2),
            self.on_next(150, 3),
            self.on_next(200, 4),
            self.on_completed(250),
        )
        n = [0]

        def create():
            def condition(x):
                n[0] += 1
                return n[0] < 3

            return xs.pipe(ops.do_while(condition))

        results = scheduler.start(create=create)

        assert results.messages == [
            self.on_next(250, 1),
            self.on_next(300, 2),
            self.on_next(350, 3),
            self.on_next(400, 4),
            self.on_next(500, 1),
            self.on_next(550, 2),
            self.on_next(600, 3),
            self.on_next(650, 4),
            self.on_next(750, 1),
            self.on_next(800, 2),
            self.on_next(850, 3),
            self.on_next(900, 4),
            self.on_completed(950),
        ]
        assert xs.subscriptions == [
            self.subscribe(200, 450),
            self.subscribe(450, 700),
            self.subscribe(700, 950),
        ]

    def test_dowhile_sometimes_throws(self):
        ex = "ex"
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(
            self.on_next(50, 1),
            self.on_next(100, 2),
            self.on_next(150, 3),
            self.on_next(200, 4),
            self.on_completed(250),
        )
        n = [0]

        def create():
            def condition(x):
                n[0] += 1
                if n[0] < 3:
                    return True
                else:
                    raise Exception(ex)

            return xs.pipe(ops.do_while(condition))

        results = scheduler.start(create=create)

        assert results.messages == [
            self.on_next(250, 1),
            self.on_next(300, 2),
            self.on_next(350, 3),
            self.on_next(400, 4),
            self.on_next(500, 1),
            self.on_next(550, 2),
            self.on_next(600, 3),
            self.on_next(650, 4),
            self.on_next(750, 1),
            self.on_next(800, 2),
            self.on_next(850, 3),
            self.on_next(900, 4),
            self.on_error(950, ex),
        ]
        assert xs.subscriptions == [
            self.subscribe(200, 450),
            self.subscribe(450, 700),
            self.subscribe(700, 950),
        ]
