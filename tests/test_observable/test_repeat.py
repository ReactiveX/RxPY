import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

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


class TestRepeat(unittest.TestCase):
    def test_repeat_value_count_zero(self):
        scheduler = TestScheduler()

        def create():
            return Observable.repeat_value(42, 0)
        results = scheduler.start(create)

        assert results.messages == [close(200)]

    def test_repeat_value_count_one(self):
        scheduler = TestScheduler()

        def create():
            return Observable.repeat_value(42, 1)

        results = scheduler.start(create)
        assert results.messages == [send(200, 42), close(200)]

    def test_repeat_value_count_ten(self):
        scheduler = TestScheduler()

        def create():
            return Observable.repeat_value(42, 10)

        results = scheduler.start(create)
        assert results.messages == [send(200, 42), send(200, 42), send(200, 42), send(200, 42), send(200, 42), send(200, 42), send(200, 42), send(200, 42), send(200, 42), send(200, 42), close(200)]

    def test_repeat_value_count_dispose(self):
        scheduler = TestScheduler()

        def create():
            return Observable.repeat_value(42, 10)

        results = scheduler.start(create, disposed=200)
        assert results.messages == []

    def test_repeat_value(self):
        scheduler = TestScheduler()

        def create():
            return Observable.repeat_value(42, -1)

        results = scheduler.start(create, disposed=201)
        assert results.messages[:6] == [send(200, 42), send(200, 42), send(200, 42), send(200, 42), send(200, 42), send(200, 42)]

    def test_repeat_observable_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 1),
                                              send(200, 3),
                                              send(150, 2),
                                              close(250))
        results = scheduler.start(lambda: xs.repeat())

        assert results.messages == [send(300, 1),
                                    send(350, 2),
                                    send(400, 3),
                                    send(550, 1),
                                    send(600, 2),
                                    send(650, 3),
                                    send(800, 1),
                                    send(850, 2),
                                    send(900, 3)]
        assert xs.subscriptions == [subscribe(200, 450),
                                    subscribe(450, 700),
                                    subscribe(700, 950),
                                    subscribe(950, 1000)]

    def test_repeat_observable_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3))
        results = scheduler.start(lambda: xs.repeat())

        assert results.messages == [send(300, 1), send(350, 2), send(400, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_repeat_observable_error(self):
        results = None
        scheduler = TestScheduler()
        ex = 'ex'
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3), throw(250, ex))
        results = scheduler.start(lambda: xs.repeat())

        assert results.messages == [send(300, 1), send(350, 2), send(400, 3), throw(450, ex)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_repeat_observable_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.return_value(11).repeat()
        xs.subscribe_(lambda x: _raise('ex'), scheduler=scheduler1)

        with self.assertRaises(RxException):
            scheduler1.start()

        scheduler2 = TestScheduler()
        ys = Observable.throw('ex').repeat()
        ys.subscribe_(lambda ex: _raise('ex'), scheduler=scheduler2)

        with self.assertRaises(Exception):
            scheduler2.start()

        scheduler3 = TestScheduler()
        zs = Observable.return_value(1).repeat()
        d = zs.subscribe_(close=lambda: _raise('ex'), scheduler=scheduler3)

        scheduler3.schedule_absolute(210, lambda sc, st: d.dispose())
        scheduler3.start()

        # scheduler4 = TestScheduler()
        # xss = Observable.create(lambda o: _raise('ex')).repeat()
        # with self.assertRaises(RxException):
        #     xss.subscribe(scheduler=scheduler4)

    def test_repeat_observable_repeat_count_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(5, 1), send(10, 2), send(15, 3), close(20))
        results = scheduler.start(lambda: xs.repeat(3))

        assert results.messages == [send(205, 1), send(210, 2), send(215, 3), send(225, 1), send(230, 2), send(235, 3), send(245, 1), send(250, 2), send(255, 3), close(260)]
        assert xs.subscriptions == [subscribe(200, 220), subscribe(220, 240), subscribe(240, 260)]

    def test_repeat_observable_repeat_count_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(5, 1), send(10, 2), send(15, 3), close(20))
        results = scheduler.start(lambda: xs.repeat(3), disposed=231)
        assert results.messages == [send(205, 1), send(210, 2), send(215, 3), send(225, 1), send(230, 2)]
        assert xs.subscriptions == [subscribe(200, 220), subscribe(220, 231)]

    def test_repeat_observable_repeat_count_infinite(self):
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3))
        results = scheduler.start(lambda: xs.repeat(3))

        assert results.messages == [send(300, 1), send(350, 2), send(400, 3)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_repeat_observable_repeat_count_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_cold_observable(send(100, 1), send(150, 2), send(200, 3), throw(250, ex))
        results = scheduler.start(lambda: xs.repeat(3))

        assert results.messages == [send(300, 1), send(350, 2), send(400, 3), throw(450, ex)]
        assert xs.subscriptions == [subscribe(200, 450)]

    def test_repeat_observable_repeat_count_throws(self):
        scheduler1 = TestScheduler()
        xs = Observable.return_value(1).repeat(3)
        xs.subscribe_(lambda x: _raise('ex'), scheduler=scheduler1)

        with self.assertRaises(RxException):
            scheduler1.start()

        scheduler2 = TestScheduler()
        ys = Observable.throw('ex1').repeat(3)
        ys.subscribe_(throw=lambda ex: _raise('ex2'), scheduler=scheduler2)

        with self.assertRaises(RxException):
            scheduler2.start()

        # scheduler3 = TestScheduler()
        # zs = Observable.return_value(1).repeat(100)
        # d = zs.subscribe_(close=lambda: _raise('ex3'), scheduler=scheduler3)

        # scheduler3.schedule_absolute(10, lambda sc, st: d.dispose())
        # scheduler3.start()

    #     xss = Observable.create(lambda o: _raise('ex4')).repeat(3)
    #     with self.assertRaises(RxException):
    #         xss.subscribe()

