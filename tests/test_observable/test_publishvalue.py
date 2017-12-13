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


class TestPublishValue(unittest.TestCase):

    def test_publishwithinitialvalue_basic(self):
        subscription = [None]
        connection = [None]
        ys = [None]

        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish_value(1979)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(subscribed, action1)

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
        assert results.messages == [
            send(200, 1979),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(520, 11)]
        assert xs.subscriptions == [
            subscribe(300, 400),
            subscribe(500, 550),
            subscribe(650, 800)]

    def test_publish_with_initial_value_error(self):
        connection = [None]
        subscription = [None]
        ys = [None]

        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            throw(600, ex))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish_value(1979)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(subscribed, action1)

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
        assert results.messages == [
            send(200, 1979),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(520, 11),
            send(560, 20),
            throw(600, ex)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_publish_with_initial_value_complete(self):
        connection = [None]
        subscription = [None]
        ys = [None]
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish_value(1979)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(subscribed, action1)

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
        assert results.messages == [
            send(200, 1979),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(520, 11),
            send(560, 20),
            close(600)]
        assert xs.subscriptions == [subscribe(300, 400), subscribe(500, 600)]

    def test_publish_with_initial_value_dispose(self):
        connection = [None]
        subscription = [None]
        ys = [None]

        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))

        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish_value(1979)
        scheduler.schedule_absolute(created, action0)

        def action1(scheduler, state):
            subscription[0] = ys[0].subscribe(results)
        scheduler.schedule_absolute(subscribed, action1)

        def action2(scheduler, state):
            subscription[0].dispose()
        scheduler.schedule_absolute(350, action2)

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
        assert results.messages == [
            send(200, 1979),
            send(340, 8)]
        assert xs.subscriptions == [
            subscribe(300, 400),
            subscribe(500, 550),
            subscribe(650, 800)]

    def test_publish_with_initial_value_multiple_connections(self):
        xs = Observable.never()
        ys = xs.publish_value(1979)
        connection1 = ys.connect()
        connection2 = ys.connect()
        assert(connection1 == connection2)
        connection1.dispose()
        connection2.dispose()
        connection3 = ys.connect()
        assert(connection1 != connection3)

    def test_publish_with_initial_value_lambda_zip_complete(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))

        def create():
            def selector(_xs):
                return _xs.zip(_xs.skip(1), lambda prev, cur: cur + prev)
            return xs.publish_value(1979, selector)
        results = scheduler.start(create)

        assert results.messages == [
            send(220, 1982),
            send(280, 7),
            send(290, 5),
            send(340, 9),
            send(360, 13),
            send(370, 11),
            send(390, 13),
            send(410, 20),
            send(430, 15),
            send(450, 11),
            send(520, 20),
            send(560, 31),
            close(600)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_publish_with_initial_value_lambda_zip_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            throw(600, ex))

        def create():
            def selector(_xs):
                return _xs.zip(_xs.skip(1), lambda prev, cur: cur + prev)
            return xs.publish_value(1979, selector)

        results = scheduler.start(create)

        assert results.messages == [
            send(220, 1982),
            send(280, 7),
            send(290, 5),
            send(340, 9),
            send(360, 13),
            send(370, 11),
            send(390, 13),
            send(410, 20),
            send(430, 15),
            send(450, 11),
            send(520, 20),
            send(560, 31),
            throw(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_publish_with_initial_value_lambda_zip_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(110, 7),
            send(220, 3),
            send(280, 4),
            send(290, 1),
            send(340, 8),
            send(360, 5),
            send(370, 6),
            send(390, 7),
            send(410, 13),
            send(430, 2),
            send(450, 9),
            send(520, 11),
            send(560, 20),
            close(600))

        def create():
            def selector(_xs):
                return _xs.zip(_xs.skip(1), lambda prev, cur: cur + prev)
            return xs.publish_value(1979, selector)

        results = scheduler.start(create, disposed=470)
        assert results.messages == [
            send(220, 1982),
            send(280, 7),
            send(290, 5),
            send(340, 9),
            send(360, 13),
            send(370, 11),
            send(390, 13),
            send(410, 20),
            send(430, 15),
            send(450, 11)]
        assert xs.subscriptions == [subscribe(200, 470)]
