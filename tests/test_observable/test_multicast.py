import unittest

from rx.subjects import Subject
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestMulticast(unittest.TestCase):
    def test_multicast_hot_1(self):
        scheduler = TestScheduler()

        s = Subject()

        xs = scheduler.create_hot_observable(
            on_next(40, 0),
            on_next(90, 1),
            on_next(150, 2),
            on_next(210, 3),
            on_next(240, 4),
            on_next(270, 5),
            on_next(330, 6),
            on_next(340, 7),
            on_completed(390))

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
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(200, action1)

        def action2(scheduler, state):
            d1[0].dispose()
        scheduler.schedule_absolute(300, action2)

        scheduler.start()

        o.messages.assert_equal(
            on_next(210, 3),
            on_next(240, 4),
            on_next(270, 5)
        )
        xs.subscriptions.assert_equal(subscribe(200, 390))

    def test_multicast_hot_2(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_completed(390))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(200, action2)

        def action3(scheduler, state):
            return d1[0].dispose()
        scheduler.schedule_absolute(300, action3)

        scheduler.start()
        o.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(270, 5))
        xs.subscriptions.assert_equal(subscribe(100, 390))

    def test_multicast_hot_21(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_completed(390))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(200, action2)

        def action3(scheduler, state):
            return d1[0].dispose()
        scheduler.schedule_absolute(300, action3)

        scheduler.start()
        o.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(270, 5))
        xs.subscriptions.assert_equal(subscribe(100, 390))

    def test_multicast_hot_3(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_completed(390))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(200, action2)

        def action3(scheduler, state):
            d2[0].dispose()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(335, action4)

        scheduler.start()
        o.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(340, 7), on_completed(390))
        xs.subscriptions.assert_equal(subscribe(100, 300), subscribe(335, 390))

    def test_multicast_hot_4(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_error(390, ex))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(200, action2)

        def action3(scheduler, state):
            d2[0].dispose()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(335, action4)

        scheduler.start()
        o.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(340, 7), on_error(390, ex))
        xs.subscriptions.assert_equal(subscribe(100, 300), subscribe(335, 390))

    def test_multicast_hot_5(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_error(390, ex))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(400, action2)

        scheduler.start()
        o.messages.assert_equal(on_error(400, ex))
        xs.subscriptions.assert_equal(subscribe(100, 390))

    def test_multicast_hot_6(self):
        c = [None]
        d1 = [None]
        d2 = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_completed(390))
        s = Subject()
        o = scheduler.create_observer()

        def action0(scheduler, state):
            c[0] = xs.multicast(s)
        scheduler.schedule_absolute(50, action0)

        def action1(scheduler, state):
            d2[0] = c[0].connect()
        scheduler.schedule_absolute(100, action1)

        def action2(scheduler, state):
            d1[0] = c[0].subscribe(o)
        scheduler.schedule_absolute(400, action2)

        scheduler.start()
        o.messages.assert_equal(on_completed(400))
        xs.subscriptions.assert_equal(subscribe(100, 390))

    def test_multicast_cold_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_completed(390))

        def create():
            def subject_selector():
                return Subject()
            def selector(ys):
                return ys
            return xs.multicast(subject_selector=subject_selector, selector=selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_completed(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))

    def test_multicast_cold_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_error(390, ex))

        def create():
            def subject_selector():
                return Subject()
            def selector(ys):
                return ys
            return xs.multicast(subject_selector=subject_selector, selector=selector)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_error(390, ex))
        xs.subscriptions.assert_equal(subscribe(200, 390))

    def test_multicast_cold_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7))

        def create():
            def subject_selector():
                return Subject()
            def selector(ys):
                return ys
            return xs.multicast(subject_selector=subject_selector, selector=selector)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_multicast_cold_zip(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(40, 0), on_next(90, 1), on_next(150, 2), on_next(210, 3), on_next(240, 4), on_next(270, 5), on_next(330, 6), on_next(340, 7), on_completed(390))

        def create():
            def subject_selector():
                return Subject()
            def selector(ys):
                return ys.zip(ys, lambda a,b: a+b)
            return xs.multicast(subject_selector=subject_selector, selector=selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 6), on_next(240, 8), on_next(270, 10), on_next(330, 12), on_next(340, 14), on_completed(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
