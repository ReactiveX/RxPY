import unittest

import rx
from rx import operators as ops
from rx.internal.utils import subscribe as _subscribe
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
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(
            370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.replay(buffer_size=3, scheduler=scheduler))
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = _subscribe(ys[0], results, scheduler=scheduler)
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
        assert results.messages == [on_next(450, 5), on_next(450, 6), on_next(450, 7), on_next(520, 11)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 550), subscribe(650, 800)]

    def test_replay_count_error(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(
            370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_error(600, ex))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.replay(buffer_size=3, scheduler=scheduler))
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = _subscribe(ys[0], results)
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
        assert results.messages == [on_next(450, 5), on_next(450, 6), on_next(
            450, 7), on_next(520, 11), on_next(560, 20), on_error(600, ex)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_replay_count_complete(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(
            370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.replay(buffer_size=3, scheduler=scheduler))
        scheduler.schedule_absolute(created, action0)

        def action1(scehduler, state):
            subscription[0] = _subscribe(ys[0], results)
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
        assert results.messages == [on_next(450, 5), on_next(450, 6), on_next(
            450, 7), on_next(520, 11), on_next(560, 20), on_completed(600)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_replay_count_dispose(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(
            370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.replay(buffer_size=3, scheduler=scheduler))
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = _subscribe(ys[0], results)
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
        assert results.messages == [on_next(450, 5), on_next(450, 6), on_next(450, 7)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 550), subscribe(650, 800)]

    def test_replay_count_multiple_connections(self):

        xs = rx.never()
        ys = xs.pipe(ops.replay(None, 3))
        connection1 = ys.connect()
        connection2 = ys.connect()
        assert connection1 == connection2
        connection1.dispose()
        connection2.dispose()
        connection3 = ys.connect()
        assert connection1 != connection3

    # def test_replay_count_lambda_zip_complete(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))

    #     def action():
    #         def mapper(_xs):
    #             return _xs.take(6).repeat()
    #         return xs.replay(mapper, 3, scheduler=scheduler)

    #     results = scheduler.start(action, disposed=610)
    #     assert results.messages == [on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(370, 8), on_next(370, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(430, 7), on_next(430, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_next(560, 9), on_next(560, 11), on_next(560, 20), on_next(600, 9), on_next(600, 11), on_next(600, 20), on_next(600, 9), on_next(600, 11), on_next(600, 20)]
    #     assert xs.subscriptions == [subscribe(200, 600)]

    # def test_replay_count_lambda_zip_error(self):
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_error(600, ex))

    #     def create():
    #         def mapper(_xs):
    #             return _xs.take(6).repeat()

    #         return xs.replay(mapper, 3, None)

    #     results = scheduler.start(create)

    #     assert results.messages == [on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_next(562, 9), on_next(563, 11), on_next(564, 20), on_error(600, ex)]
    #     assert xs.subscriptions == [subscribe(200, 600)]

    # def test_replay_count_lambda_zip_dispose(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))

    #     def create():
    #         def mapper(_xs):
    #             return _xs.take(6).repeat()

    #         return xs.replay(mapper, 3, None)

    #     results = scheduler.start(create, disposed=470)
    #     assert results.messages == [on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(450, 9)]
    #     assert xs.subscriptions == [subscribe(200, 470)]

    def test_replay_time_basic(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(
            370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.replay(window=150, scheduler=scheduler))
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = _subscribe(ys[0], results)
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
        assert results.messages == [on_next(450, 8), on_next(
            450, 5), on_next(450, 6), on_next(450, 7), on_next(520, 11)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 550), subscribe(650, 800)]

    def test_replay_time_error(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(
            370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_error(600, ex))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.replay(window=75, scheduler=scheduler))
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = _subscribe(ys[0], results, scheduler=scheduler)
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
        assert results.messages == [on_next(450, 7), on_next(520, 11), on_next(560, 20), on_error(600, ex)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_replay_time_complete(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(
            370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.replay(window=85, scheduler=scheduler))
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = _subscribe(ys[0], results, scheduler=scheduler)
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
        assert results.messages == [on_next(450, 6), on_next(
            450, 7), on_next(520, 11), on_next(560, 20), on_completed(600)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_replay_time_dispose(self):
        subscription = [None]
        connection = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(
            370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.pipe(ops.replay(window=100, scheduler=scheduler))
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = _subscribe(ys[0], results, scheduler=scheduler)
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
        assert results.messages == [on_next(450, 5), on_next(450, 6), on_next(450, 7)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 550), subscribe(650, 800)]

    def test_replay_time_multiple_connections(self):
        xs = rx.never()
        ys = xs.pipe(ops.replay(window=100))
        connection1 = ys.connect()
        connection2 = ys.connect()
        assert connection1 == connection2
        connection1.dispose()
        connection2.dispose()
        connection3 = ys.connect()
        assert connection1 != connection3

    # def test_replay_time_lambda_zip_complete(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(
    #         on_next(110, 7), on_next(220, 3), on_next(280, 4),
    #         on_next(290, 1), on_next(340, 8), on_next(360, 5),
    #         on_next(370, 6), on_next(390, 7), on_next(410, 13),
    #         on_next(430, 2), on_next(450, 9), on_next(520, 11),
    #         on_next(560, 20), on_completed(600))

    #     def create():
    #         def mapper(_xs):
    #             return _xs.pipe(
    #                 ops.take(6),
    #                 ops.repeat()
    #             )
    #         return xs.pipe(ops.replay(mapper, None, 50))

    #     results = scheduler.start(create, disposed=610)
    #     assert results.messages == [
    #         on_next(220, 3), on_next(280, 4), on_next(290, 1),
    #         on_next(340, 8), on_next(360, 5), on_next(370, 6),
    #         on_next(370, 8), on_next(370, 5), on_next(370, 6),
    #         on_next(390, 7), on_next(410, 13), on_next(430, 2),
    #         on_next(430, 7), on_next(430, 13), on_next(430, 2),
    #         on_next(450, 9), on_next(520, 11), on_next(560, 20),
    #         on_next(560, 11), on_next(560, 20), on_next(600, 20),
    #         on_next(600, 20), on_next(600, 20), on_next(600, 20)]
    #     assert xs.subscriptions == [subscribe(200, 600)]

    # def test_replay_time_lambda_zip_error(self):
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_error(600, ex))

    #     def create():
    #         def mapper(_xs):
    #             return _xs.take(6).repeat()

    #         return xs.replay(mapper, None, 50)

    #     results = scheduler.start(create)

    #     assert results.messages == [on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_next(562, 11), on_next(563, 20), on_error(600, ex)]
    #     assert xs.subscriptions == [subscribe(200, 600)]

    # def test_replay_time_lambda_zip_dispose(self):
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(110, 7), on_next(220, 3), on_next(280, 4), on_next(290, 1), on_next(340, 8), on_next(360, 5), on_next(370, 6), on_next(390, 7), on_next(410, 13), on_next(430, 2), on_next(450, 9), on_next(520, 11), on_next(560, 20), on_completed(600))
    #     def create():
    #         def mapper(_xs):
    #             return _xs.take(6).repeat()
    #         return xs.replay(mapper, None, 50)

    #     results = scheduler.start(create, disposed=470)
    #     assert results.messages == [on_next(221, 3), on_next(281, 4), on_next(291, 1), on_next(341, 8), on_next(361, 5), on_next(371, 6), on_next(372, 8), on_next(373, 5), on_next(374, 6), on_next(391, 7), on_next(411, 13), on_next(431, 2), on_next(432, 7), on_next(433, 13), on_next(434, 2), on_next(450, 9)]
    #     assert xs.subscriptions == [subscribe(200, 470)]
