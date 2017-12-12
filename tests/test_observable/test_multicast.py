import unittest

from rx.subjects import Subject
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestMulticast(unittest.TestCase):
    def test_multicast_hot_1(self):
        scheduler = TestScheduler()

        s = Subject()

        xs = scheduler.create_hot_observable(
            send(40, 0),
            send(90, 1),
            send(150, 2),
            send(210, 3),
            send(240, 4),
            send(270, 5),
            send(330, 6),
            send(340, 7),
            close(390))

        o = scheduler.create_observer()
        d1 = [None]
        d2 = [None]
        c = [None]

        def action(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action)

        def action0(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(100, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(200, action1)

        def action2(scheduler, state):
            d1[0].dispose()
        scheduler.schedule_absolute(300, action2)

        scheduler.start()

        o.messages.assert_equal(
            send(210, 3),
            send(240, 4),
            send(270, 5)
        )
        xs.subscriptions.assert_equal(subscribe(200, 390))

    def test_multicast_hot_2(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), close(390))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(200, action2)

        def action3(scheduler, state):
            return d1[0].dispose()
        scheduler.schedule_absolute(300, action3)

        scheduler.start()
        o.messages.assert_equal(send(210, 3), send(240, 4), send(270, 5))
        xs.subscriptions.assert_equal(subscribe(100, 390))

    def test_multicast_hot_21(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), close(390))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(200, action2)

        def action3(scheduler, state):
            return d1[0].dispose()
        scheduler.schedule_absolute(300, action3)

        scheduler.start()
        o.messages.assert_equal(send(210, 3), send(240, 4), send(270, 5))
        xs.subscriptions.assert_equal(subscribe(100, 390))

    def test_multicast_hot_3(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), close(390))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(200, action2)

        def action3(scheduler, state):
            d2[0].dispose()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(335, action4)

        scheduler.start()
        o.messages.assert_equal(send(210, 3), send(240, 4), send(270, 5), send(340, 7), close(390))
        xs.subscriptions.assert_equal(subscribe(100, 300), subscribe(335, 390))

    def test_multicast_hot_4(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), throw(390, ex))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(200, action2)

        def action3(scheduler, state):
            d2[0].dispose()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(335, action4)

        scheduler.start()
        o.messages.assert_equal(send(210, 3), send(240, 4), send(270, 5), send(340, 7), throw(390, ex))
        xs.subscriptions.assert_equal(subscribe(100, 300), subscribe(335, 390))

    def test_multicast_hot_5(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), throw(390, ex))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(400, action2)

        scheduler.start()
        o.messages.assert_equal(throw(400, ex))
        xs.subscriptions.assert_equal(subscribe(100, 390))

    def test_multicast_hot_6(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), close(390))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect(scheduler)
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(400, action2)

        scheduler.start()
        o.messages.assert_equal(close(400))
        xs.subscriptions.assert_equal(subscribe(100, 390))

    def test_multicast_cold_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), close(390))

        def create():
            def subject_selector(scheduler):
                return Subject()
            def selector(ys):
                return ys
            return xs.multicast(subject_selector=subject_selector, selector=selector)
        results = scheduler.start(create)

        results.messages.assert_equal(send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), close(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))

    def test_multicast_cold_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), throw(390, ex))

        def create():
            def subject_selector(scheduler):
                return Subject()
            def selector(ys):
                return ys
            return xs.multicast(subject_selector=subject_selector, selector=selector)

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), throw(390, ex))
        xs.subscriptions.assert_equal(subscribe(200, 390))

    def test_multicast_cold_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7))

        def create():
            def subject_selector(scheduler):
                return Subject()
            def selector(ys):
                return ys
            return xs.multicast(subject_selector=subject_selector, selector=selector)

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_multicast_cold_zip(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(40, 0), send(90, 1), send(150, 2), send(210, 3), send(240, 4), send(270, 5), send(330, 6), send(340, 7), close(390))

        def create():
            def subject_selector(scheduler):
                return Subject()
            def selector(ys):
                return ys.zip(ys, lambda a,b: a+b)
            return xs.multicast(subject_selector=subject_selector, selector=selector)
        results = scheduler.start(create)

        results.messages.assert_equal(send(210, 6), send(240, 8), send(270, 10), send(330, 12), send(340, 14), close(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
