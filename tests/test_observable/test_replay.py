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


class TestReplay(unittest.TestCase):
    def test_replay_count_basic(self):
        connection = [None]
        subscription = [None]
        ys = [None]

        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, 3, None)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results, scheduler)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        results.messages.assert_equal(send(450, 5), send(450, 6), send(450, 7), send(520, 11))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))

    def test_replay_count_error(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), throw(600, ex))
        results = scheduler.create_observer()

        def action0(scheduler, state):
             ys[0] = xs.replay(None, 3, None)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action6)

        scheduler.start()
        results.messages.assert_equal(send(450, 5), send(450, 6), send(450, 7), send(520, 11), send(560, 20), throw(600, ex))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))

    def test_replay_count_complete(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, 3, None)
        scheduler.schedule_absolute(created, action0)

        def action1(scehduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(500, action5)

        def action(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action)

        scheduler.start()
        results.messages.assert_equal(send(450, 5), send(450, 6), send(450, 7), send(520, 11), send(560, 20), close(600))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))

    def test_replay_count_dispose(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, 3, None)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(475, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        results.messages.assert_equal(send(450, 5), send(450, 6), send(450, 7))
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

    # def test_replay_count_lambda_zip_complete(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))

    #     def action():
    #         def selector(_xs):
    #             return _xs.take(6).repeat()
    #         return xs.replay(selector, 3, None)

    #     results = scheduler.start(action, disposed=610)
    #     results.messages.assert_equal(send(221, 3), send(281, 4), send(291, 1), send(341, 8), send(361, 5), send(371, 6), send(372, 8), send(373, 5), send(374, 6), send(391, 7), send(411, 13), send(431, 2), send(432, 7), send(433, 13), send(434, 2), send(450, 9), send(520, 11), send(560, 20), send(562, 9), send(563, 11), send(564, 20), send(602, 9), send(603, 11), send(604, 20), send(606, 9), send(607, 11), send(608, 20))
    #     xs.subscriptions.assert_equal(subscribe(200, 600))

    # def test_replay_count_lambda_zip_error(self):
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), throw(600, ex))

    #     def create():
    #         def selector(_xs):
    #             return _xs.take(6).repeat()

    #         return xs.replay(selector, 3, None)

    #     results = scheduler.start(create)

    #     results.messages.assert_equal(send(221, 3), send(281, 4), send(291, 1), send(341, 8), send(361, 5), send(371, 6), send(372, 8), send(373, 5), send(374, 6), send(391, 7), send(411, 13), send(431, 2), send(432, 7), send(433, 13), send(434, 2), send(450, 9), send(520, 11), send(560, 20), send(562, 9), send(563, 11), send(564, 20), throw(600, ex))
    #     xs.subscriptions.assert_equal(subscribe(200, 600))

    # def test_replay_count_lambda_zip_dispose(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))

    #     def create():
    #         def selector(_xs):
    #             return _xs.take(6).repeat()

    #         return xs.replay(selector, 3, None)

    #     results = scheduler.start(create, disposed=470)
    #     results.messages.assert_equal(send(221, 3), send(281, 4), send(291, 1), send(341, 8), send(361, 5), send(371, 6), send(372, 8), send(373, 5), send(374, 6), send(391, 7), send(411, 13), send(431, 2), send(432, 7), send(433, 13), send(434, 2), send(450, 9))
    #     xs.subscriptions.assert_equal(subscribe(200, 470))

    def test_replay_time_basic(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, None, 150)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(550, action6)

        def action7(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(650, action7)

        def action8(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action8)

        scheduler.start()
        results.messages.assert_equal(send(450, 8), send(450, 5), send(450, 6), send(450, 7), send(520, 11))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))

    def test_replay_time_error(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), throw(600, ex))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.replay(None, None, 75)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results, scheduler)
        scheduler.schedule_absolute(450, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(disposed, action2)

        def action3(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(300, action3)

        def action4(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(400, action4)

        def action5(scheduler, state):
            connection[0] = ys[0].connect(scheduler)
        scheduler.schedule_absolute(500, action5)

        def action6(scheduler, state):
            connection[0].dispose()
        scheduler.schedule_absolute(800, action6)

        scheduler.start()
        results.messages.assert_equal(send(450, 7), send(520, 11), send(560, 20), throw(600, ex))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))

    # def test_replay_time_complete(self):
    #     subscription = [None]
    #     connection = [None]
    #     ys = [None]
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))
    #     results = scheduler.create_observer()

    #     def action0(scheduler, state):
    #         ys[0] = xs.replay(None, None, 85)
    #     scheduler.schedule_absolute(created, action0)

    #     def action1(scheduler, state):
    #         subscription[0] = ys[0].subscribe(results)
    #     scheduler.schedule_absolute(450, action1)

    #     def action2(scheduler, state):
    #         subscription[0].dispose()
    #     scheduler.schedule_absolute(disposed, action2)

    #     def action3(scheduler, state):
    #         connection[0] = ys[0].connect()
    #     scheduler.schedule_absolute(300, action3)

    #     def action4(scheduler, state):
    #         connection[0].dispose()
    #     scheduler.schedule_absolute(400, action4)

    #     def action5(scheduler, state):
    #         connection[0] = ys[0].connect()
    #     scheduler.schedule_absolute(500, action5)

    #     def action6(scheduler, state):
    #         connection[0].dispose()
    #     scheduler.schedule_absolute(800, action6)

    #     scheduler.start()
    #     results.messages.assert_equal(send(450, 6), send(450, 7), send(520, 11), send(560, 20), close(600))
    #     xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))

    # def test_replay_time_dispose(self):
    #     subscription = [None]
    #     connection = [None]
    #     ys = [None]
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))
    #     results = scheduler.create_observer()

    #     def action0(scheduler, state):
    #         ys[0] = xs.replay(None, None, 100)
    #     scheduler.schedule_absolute(created, action0)

    #     def action1(scheduler, state):
    #         subscription[0] = ys[0].subscribe(results)
    #     scheduler.schedule_absolute(450, action1)

    #     def action2(scheduler, state):
    #         subscription[0].dispose()
    #     scheduler.schedule_absolute(475, action2)

    #     def action3(scheduler, state):
    #         connection[0] = ys[0].connect()
    #     scheduler.schedule_absolute(300, action3)

    #     def action4(scheduler, state):
    #         connection[0].dispose()
    #     scheduler.schedule_absolute(400, action4)

    #     def action5(scheduler, state):
    #         connection[0] = ys[0].connect()
    #     scheduler.schedule_absolute(500, action5)

    #     def action6(scheduler, state):
    #         connection[0].dispose()
    #     scheduler.schedule_absolute(550, action6)

    #     def action7(scheduler, state):
    #         connection[0] = ys[0].connect()
    #     scheduler.schedule_absolute(650, action7)

    #     def action8(scheduler, state):
    #         connection[0].dispose()
    #     scheduler.schedule_absolute(800, action8)

    #     scheduler.start()
    #     results.messages.assert_equal(send(450, 5), send(450, 6), send(450, 7))
    #     xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))

    # def test_replay_time_multiple_connections(self):
    #     xs = Observable.never()
    #     ys = xs.replay(None, None, 100)
    #     connection1 = ys.connect()
    #     connection2 = ys.connect()
    #     assert(connection1 == connection2)
    #     connection1.dispose()
    #     connection2.dispose()
    #     connection3 = ys.connect()
    #     assert(connection1 != connection3)

    # def test_replay_time_lambda_zip_complete(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))

    #     def create():
    #         def selector(_xs):
    #             return _xs.take(6).repeat()
    #         return xs.replay(selector, None, 50)

    #     results = scheduler.start(create, disposed=610)
    #     results.messages.assert_equal(send(221, 3), send(281, 4), send(291, 1), send(341, 8), send(361, 5), send(371, 6), send(372, 8), send(373, 5), send(374, 6), send(391, 7), send(411, 13), send(431, 2), send(432, 7), send(433, 13), send(434, 2), send(450, 9), send(520, 11), send(560, 20), send(562, 11), send(563, 20), send(602, 20), send(604, 20), send(606, 20), send(608, 20))
    #     xs.subscriptions.assert_equal(subscribe(200, 600))

    # def test_replay_time_lambda_zip_error(self):
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), throw(600, ex))

    #     def create():
    #         def selector(_xs):
    #             return _xs.take(6).repeat()

    #         return xs.replay(selector, None, 50)

    #     results = scheduler.start(create)

    #     results.messages.assert_equal(send(221, 3), send(281, 4), send(291, 1), send(341, 8), send(361, 5), send(371, 6), send(372, 8), send(373, 5), send(374, 6), send(391, 7), send(411, 13), send(431, 2), send(432, 7), send(433, 13), send(434, 2), send(450, 9), send(520, 11), send(560, 20), send(562, 11), send(563, 20), throw(600, ex))
    #     xs.subscriptions.assert_equal(subscribe(200, 600))

    # def test_replay_time_lambda_zip_dispose(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(send(110, 7), send(220, 3), send(280, 4), send(290, 1), send(340, 8), send(360, 5), send(370, 6), send(390, 7), send(410, 13), send(430, 2), send(450, 9), send(520, 11), send(560, 20), close(600))
    #     def create():
    #         def selector(_xs):
    #             return _xs.take(6).repeat()
    #         return xs.replay(selector, None, 50)

    #     results = scheduler.start(create, disposed=470)
    #     results.messages.assert_equal(send(221, 3), send(281, 4), send(291, 1), send(341, 8), send(361, 5), send(371, 6), send(372, 8), send(373, 5), send(374, 6), send(391, 7), send(411, 13), send(431, 2), send(432, 7), send(433, 13), send(434, 2), send(450, 9))
    #     xs.subscriptions.assert_equal(subscribe(200, 470))

