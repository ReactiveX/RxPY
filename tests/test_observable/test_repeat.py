import unittest

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

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


class TestRepeat(unittest.TestCase):
    def test_repeat_value_count_zero(self):
        scheduler = TestScheduler()

        def create():
            return rx.repeat_value(42, 0)
        results = scheduler.start(create)

        assert results.messages == [on_completed(200)]

    def test_repeat_value_count_one(self):
        scheduler = TestScheduler()

        def create():
            return rx.repeat_value(42, 1)

        results = scheduler.start(create)
        assert results.messages == [on_next(200, 42), on_completed(200)]

    def test_repeat_value_count_ten(self):
        scheduler = TestScheduler()

        def create():
            return rx.repeat_value(42, 10)

        results = scheduler.start(create)
        assert results.messages == [on_next(200, 42), on_next(200, 42), on_next(200, 42), on_next(200, 42), on_next(
            200, 42), on_next(200, 42), on_next(200, 42), on_next(200, 42), on_next(200, 42), on_next(200, 42), on_completed(200)]

    def test_repeat_value_count_dispose(self):
        scheduler = TestScheduler()

        def create():
            return rx.repeat_value(42, 10)

        results = scheduler.start(create, disposed=200)
        assert results.messages == []

    def test_repeat_value(self):
        scheduler = TestScheduler()

        def create():
            return rx.repeat_value(42, -1)

        results = scheduler.start(create, disposed=201)
        assert results.messages[:6] == [on_next(200, 42), on_next(200, 42), on_next(
            200, 42), on_next(200, 42), on_next(200, 42), on_next(200, 42)]

    def test_repeat_observable_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 1),
                                              on_next(200, 3),
                                              on_next(150, 2),
                                              on_completed(250))
        results = scheduler.start(lambda: xs.pipe(ops.repeat()))

        assert results.messages == [on_next(300, 1),
                                    on_next(350, 2),
                                    on_next(400, 3),
                                    on_next(550, 1),
                                    on_next(600, 2),
                                    on_next(650, 3),
                                    on_next(800, 1),
                                    on_next(850, 2),
                                    on_next(900, 3)]
        assert xs.subscriptions == [subscribe(200, 450),
                                    subscribe(450, 700),
                                    subscribe(700, 950),
                                    subscribe(950, 1000)]

    def test_repeat_observable_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
        results = scheduler.start(lambda: xs.pipe(ops.repeat()))

        assert results.messages == [on_next(300, 1), on_next(350, 2), on_next(400, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_repeat_observable_error(self):
        results = None
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
        results = scheduler.start(lambda: xs.pipe(ops.repeat()))

        assert results.messages == [on_next(300, 1), on_next(350, 2), on_next(400, 3), on_error(450, ex)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_repeat_observable_throws(self):
        scheduler1 = TestScheduler()
        xs = rx.return_value(11).pipe(ops.repeat())
        xs.subscribe_(lambda x: _raise('ex'), scheduler=scheduler1)

        with self.assertRaises(RxException):
            scheduler1.start()

        scheduler2 = TestScheduler()
        ys = rx.throw('ex').pipe(ops.repeat())
        ys.subscribe_(lambda ex: _raise('ex'), scheduler=scheduler2)

        with self.assertRaises(Exception):
            scheduler2.start()

        scheduler3 = TestScheduler()
        zs = rx.return_value(1).pipe(ops.repeat())
        d = zs.subscribe_(on_completed=lambda: _raise('ex'), scheduler=scheduler3)

        scheduler3.schedule_absolute(210, lambda sc, st: d.dispose())
        scheduler3.start()

        # scheduler4 = TestScheduler()
        # xss = Observable.create(lambda o: _raise('ex')).repeat()
        # with self.assertRaises(RxException):
        #     xss.subscribe(scheduler=scheduler4)

    def test_repeat_observable_repeat_count_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_completed(20))
        results = scheduler.start(lambda: xs.pipe(ops.repeat(3)))

        assert results.messages == [on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(
            230, 2), on_next(235, 3), on_next(245, 1), on_next(250, 2), on_next(255, 3), on_completed(260)]
        assert xs.subscriptions == [subscribe(200, 220), subscribe(220, 240), subscribe(240, 260)]

    def test_repeat_observable_repeat_count_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_completed(20))
        results = scheduler.start(lambda: xs.pipe(ops.repeat(3)), disposed=231)
        assert results.messages == [on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2)]
        assert xs.subscriptions == [subscribe(200, 220), subscribe(220, 231)]

    def test_repeat_observable_repeat_count_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
        results = scheduler.start(lambda: xs.pipe(ops.repeat(3)))

        assert results.messages == [on_next(300, 1), on_next(350, 2), on_next(400, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_repeat_observable_repeat_count_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
        results = scheduler.start(lambda: xs.pipe(ops.repeat(3)))

        assert results.messages == [on_next(300, 1), on_next(350, 2), on_next(400, 3), on_error(450, ex)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_repeat_observable_repeat_count_throws(self):
        scheduler1 = TestScheduler()
        xs = rx.return_value(1).pipe(ops.repeat(3))
        xs.subscribe_(lambda x: _raise('ex'), scheduler=scheduler1)

        with self.assertRaises(RxException):
            scheduler1.start()

        scheduler2 = TestScheduler()
        ys = rx.throw('ex1').pipe(ops.repeat(3))
        ys.subscribe_(on_error=lambda ex: _raise('ex2'), scheduler=scheduler2)

        with self.assertRaises(RxException):
            scheduler2.start()

        # scheduler3 = TestScheduler()
        # zs = rx.return_value(1).repeat(100)
        # d = zs.subscribe_(on_completed=lambda: _raise('ex3'), scheduler=scheduler3)

        # scheduler3.schedule_absolute(10, lambda sc, st: d.dispose())
        # scheduler3.start()

    #     xss = Observable.create(lambda o: _raise('ex4')).repeat(3)
    #     with self.assertRaises(RxException):
    #         xss.subscribe()
