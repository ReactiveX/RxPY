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


class TestReplay(unittest.TestCase):
    def test_replay_count_basic(self):
        connection = [None]
        subscription = [None]
        ys = [None]

        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, 3, None, scheduler)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        results.messages.assert_equal(on_next(451, 5), on_next(452, 6), on_next(453, 7), on_next(521, 11))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))

    def test_replay_count_error(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_error(600, ex))
        results = scheduler.create_observer()

        def action0(scheduler, state):
             ys[0] = xs.replay(None, 3, None, scheduler)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action6)

        scheduler.start()
        results.messages.assert_equal(on_next(451, 5), on_next(452, 6), on_next(453, 7), on_next(521, 11), on_next(561, 20), on_error(601, ex))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))

    def test_replay_count_complete(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, 3, None, scheduler)
        scheduler.schedule_absolute(created, action0)

        def action1(scehduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(500, action5)

        def action(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action)

        scheduler.start()
        results.messages.assert_equal(on_next(451, 5), on_next(452, 6), on_next(453, 7), on_next(521, 11), on_next(561, 20), on_completed(601))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))

    def test_replay_count_dispose(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, 3, None, scheduler)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(475, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        results.messages.assert_equal(on_next(451, 5), on_next(452, 6), on_next(453, 7))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))

    def test_replay_count_multiple_connections(self):
        xs = Observable.never()
        ys = xs.replay(None, 3)
        connection1 = ys.connect()
        connection2 = ys.connect()
        assert(connection1 == connection2)
        connection1.dispose()
        connection2.dispose()
        connection3 = ys.connect()
        assert(connection1 != connection3)

    def test_replay_count_lambda_zip_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))

        def action():
            def selector(_xs):
                return _xs.take(6).repeat()
            return xs.replay(selector, 3, None, scheduler)

        results = scheduler.start(action, disposed=610)
        results.messages.assert_equal(on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(451, 9), on_next(521, 11), on_next(561, 20), on_next(562, 9), on_next(563, 11), on_next(564, 20), on_next(602, 9), on_next(603, 11), on_next(604, 20), on_next(606, 9), on_next(607, 11), on_next(608, 20))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_replay_count_lambda_zip_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_error(600, ex))

        def create():
            def selector(_xs):
                return _xs.take(6).repeat()

            return xs.replay(selector, 3, None, scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(451, 9), on_next(521, 11), on_next(561, 20), on_next(562, 9), on_next(563, 11), on_next(564, 20), on_error(601, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_replay_count_lambda_zip_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))

        def create():
            def selector(_xs):
                return _xs.take(6).repeat()

            return xs.replay(selector, 3, None, scheduler)

        results = scheduler.start(create, disposed=470)
        results.messages.assert_equal(on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(451, 9))
        xs.subscriptions.assert_equal(subscribe(200, 470))

    def test_replay_time_basic(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, None, 150, scheduler)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        results.messages.assert_equal(on_next(451, 8), on_next(452, 5), on_next(453, 6), on_next(454, 7), on_next(521, 11))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))

    def test_replay_time_error(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_error(600, ex))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, None, 75, scheduler)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action6)

        scheduler.start()
        results.messages.assert_equal(on_next(451, 7), on_next(521, 11), on_next(561, 20), on_error(601, ex))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))

    def test_replay_time_complete(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, None, 85, scheduler)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action6)

        scheduler.start()
        results.messages.assert_equal(on_next(451, 6), on_next(452, 7), on_next(521, 11), on_next(561, 20), on_completed(601))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))

    def test_replay_time_dispose(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, None, 100, scheduler)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(475, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect()
        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        results.messages.assert_equal(on_next(451, 5), on_next(452, 6), on_next(453, 7))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))

    def test_replay_time_multiple_connections(self):
        xs = Observable.never()
        ys = xs.replay(None, None, 100)
        connection1 = ys.connect()
        connection2 = ys.connect()
        assert(connection1 == connection2)
        connection1.dispose()
        connection2.dispose()
        connection3 = ys.connect()
        assert(connection1 != connection3)

    def test_replay_time_lambda_zip_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))

        def create():
            def selector(_xs):
                return _xs.take(6).repeat()
            return xs.replay(selector, None, 50, scheduler)

        results = scheduler.start(create, disposed=610)
        results.messages.assert_equal(on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(451, 9), on_next(521, 11), on_next(561, 20), on_next(562, 11), on_next(563, 20), on_next(602, 20), on_next(604, 20), on_next(606, 20), on_next(608, 20))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_replay_time_lambda_zip_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_error(600, ex))

        def create():
            def selector(_xs):
                return _xs.take(6).repeat()

            return xs.replay(selector, None, 50, scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(451, 9), on_next(521, 11), on_next(561, 20), on_next(562, 11), on_next(563, 20), on_error(601, ex))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_replay_time_lambda_zip_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        def create():
            def selector(_xs):
                return _xs.take(6).repeat()
            return xs.replay(selector, None, 50, scheduler)

        results = scheduler.start(create, disposed=470)
        results.messages.assert_equal(on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(451, 9))
        xs.subscriptions.assert_equal(subscribe(200, 470))

