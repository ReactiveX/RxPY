import unittest

from rx import Observable
from rx.abstractobserver import AbstractObserver
from rx.linq.connectableobservable import ConnectableObservable
from rx.subjects import Subject
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable

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

class MySubject(Observable, AbstractObserver):

    def __init__(self):

        def subscribe(observer):
            self.subscribe_count += 1
            self.observer = observer

            class Duck:
                def __init__(self, this):
                    self.this = this
                def dispose(self):
                    self.this.disposed = True
            return Duck(self)

        super(MySubject, self).__init__(subscribe)

        self.dispose_on_map = {}
        self.subscribe_count = 0
        self.disposed = False

    def dispose_on(self, value, disposable):
        self.dispose_on_map[value] = disposable

    def on_next(self, value):
        self.observer.on_next(value)
        if value in self.dispose_on_map:
            self.dispose_on_map[value].dispose()

    def on_error(self, exception):
        self.observer.on_error(exception)

    def on_completed(self):
        self.observer.on_completed()

class TestPublish(unittest.TestCase):

    def test_publish_cold_zip(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(40, 0),
            on_next(90, 1),
            on_next(150, 2),
            on_next(210, 3),
            on_next(240, 4),
            on_next(270, 5),
            on_next(330, 6),
            on_next(340, 7),
            on_completed(390)
        )

        def create():
            def selector(ys):
                def result_selector(a, b):
                    return a + b
                return ys.zip(ys, result_selector)

            return xs.publish(selector=selector)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 6),
            on_next(240, 8),
            on_next(270, 10),
            on_next(330, 12),
            on_next(340, 14), on_completed(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))

    def test_ref_count_connects_on_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250)
        )
        subject = MySubject()
        conn = ConnectableObservable(xs, subject)

        def create():
            return conn.ref_count()

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(210, 1),
            on_next(220, 2),
            on_next(230, 3),
            on_next(240, 4),
            on_completed(250)
        )
        assert(subject.disposed)

    def test_ref_count_notconnected(self):
        disconnected = [False]
        count = [0]

        def factory():
            count[0] += 1

            def create(obs):
                def func():
                    disconnected[0] = True
                return func

            return Observable.create(create)

        xs = Observable.defer(factory)

        subject = MySubject()
        conn = ConnectableObservable(xs, subject)
        refd = conn.ref_count()
        dis1 = refd.subscribe()
        self.assertEqual(1, count[0])
        self.assertEqual(1, subject.subscribe_count)
        assert(not disconnected[0])
        dis2 = refd.subscribe()
        self.assertEqual(1, count[0])
        self.assertEqual(2, subject.subscribe_count)
        assert(not disconnected[0])
        dis1.dispose()
        assert(not disconnected[0])
        dis2.dispose()
        assert(disconnected[0])
        disconnected[0] = False
        dis3 = refd.subscribe()
        self.assertEqual(2, count[0])
        self.assertEqual(3, subject.subscribe_count)
        assert(not disconnected[0])
        dis3.dispose()
        assert(disconnected[0])

    def test_publish_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_completed(600)
        )
        ys = [None]
        subscription = [None]
        connection = [None]
        results = scheduler.create_observer()

        def action0(scheduler, state):
            ys[0] = xs.publish()
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
        results.messages.assert_equal(
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(520, 11)
        )
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))

    def test_publish_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(110, 7),
            on_next(220, 3),
            on_next(280, 4),
            on_next(290, 1),
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(410, 13),
            on_next(430, 2),
            on_next(450, 9),
            on_next(520, 11),
            on_next(560, 20),
            on_error(600, ex))
        
        ys = [None]
        subscription = [None]
        connection = [None]
        results = scheduler.create_observer()
        
        def action0(scheduler, state):
            ys[0] = xs.publish()
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
        results.messages.assert_equal(
            on_next(340, 8),
            on_next(360, 5),
            on_next(370, 6),
            on_next(390, 7),
            on_next(520, 11),
            on_next(560, 20), 
            on_error(600, ex))
        xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))


# def test_publish_Complete(self):
#     var connection, results, scheduler, subscription, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 7),
# on_next(220, 3),
# on_next(280, 4),
# on_next(290, 1),
# on_next(340, 8),
# on_next(360, 5),
# on_next(370, 6),
# on_next(390, 7),
# on_next(410, 13),
# on_next(430, 2),
# on_next(450, 9),
# on_next(520, 11),
# on_next(560, 20), on_completed(600))
#     results = scheduler.create_observer()
#     scheduler.schedule_absolute(created, action0)
#         ys = xs.publish()

#     scheduler.schedule_absolute(subscribed, function () {
#         subscription = ys.subscribe(results)

#     scheduler.schedule_absolute(disposed, function () {
#         subscription.dispose()

#     scheduler.schedule_absolute(300, function () {
#         connection = ys.connect()

#     scheduler.schedule_absolute(400, function () {
#         connection.dispose()

#     scheduler.schedule_absolute(500, function () {
#         connection = ys.connect()

#     scheduler.schedule_absolute(800, function () {
#         connection.dispose()

#     scheduler.start()
#     results.messages.assert_equal(on_next(340, 8),
# on_next(360, 5),
# on_next(370, 6),
# on_next(390, 7),
# on_next(520, 11),
# on_next(560, 20), on_completed(600))
#     xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 600))


# def test_publish_Dispose(self):
#     var connection, results, scheduler, subscription, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 7),
# on_next(220, 3),
# on_next(280, 4),
# on_next(290, 1),
# on_next(340, 8),
# on_next(360, 5),
# on_next(370, 6),
# on_next(390, 7),
# on_next(410, 13),
# on_next(430, 2),
# on_next(450, 9),
# on_next(520, 11),
# on_next(560, 20), on_completed(600))
#     results = scheduler.create_observer()
#     scheduler.schedule_absolute(created, function () {
#         ys = xs.publish()

#     scheduler.schedule_absolute(subscribed, function () {
#         subscription = ys.subscribe(results)

#     scheduler.schedule_absolute(350, function () {
#         subscription.dispose()

#     scheduler.schedule_absolute(300, function () {
#         connection = ys.connect()

#     scheduler.schedule_absolute(400, function () {
#         connection.dispose()

#     scheduler.schedule_absolute(500, function () {
#         connection = ys.connect()

#     scheduler.schedule_absolute(550, function () {
#         connection.dispose()

#     scheduler.schedule_absolute(650, function () {
#         connection = ys.connect()

#     scheduler.schedule_absolute(800, function () {
#         connection.dispose()

#     scheduler.start()
#     results.messages.assert_equal(on_next(340, 8))
#     xs.subscriptions.assert_equal(subscribe(300, 400), subscribe(500, 550), subscribe(650, 800))


# def test_publish_MultipleConnections(self):
#     var connection1, connection2, connection3, xs, ys
#     xs = Observable.never()
#     ys = xs.publish()
#     connection1 = ys.connect()
#     connection2 = ys.connect()
#     ok(connection1 === connection2)
#     connection1.dispose()
#     connection2.dispose()
#     connection3 = ys.connect()
#     ok(connection1 !== connection3)
#     connection3.dispose()


# test('PublishLambda_Zip_Complete(self):
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 7),
# on_next(220, 3),
# on_next(280, 4),
# on_next(290, 1),
# on_next(340, 8),
# on_next(360, 5),
# on_next(370, 6),
# on_next(390, 7),
# on_next(410, 13),
# on_next(430, 2),
# on_next(450, 9),
# on_next(520, 11),
# on_next(560, 20), on_completed(600))
#     results = scheduler.start(create)
#         return xs.publish(function (_xs) {
#             return _xs.zip(_xs.skip(1), function (prev, cur) {
#                 return cur + prev



#     results.messages.assert_equal(on_next(280, 7),
# on_next(290, 5),
# on_next(340, 9),
# on_next(360, 13),
# on_next(370, 11),
# on_next(390, 13),
# on_next(410, 20),
# on_next(430, 15),
# on_next(450, 11),
# on_next(520, 20),
# on_next(560, 31), on_completed(600))
#     xs.subscriptions.assert_equal(subscribe(200, 600))


# test('PublishLambda_Zip_Error(self):
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 7),
# on_next(220, 3),
# on_next(280, 4),
# on_next(290, 1),
# on_next(340, 8),
# on_next(360, 5),
# on_next(370, 6),
# on_next(390, 7),
# on_next(410, 13),
# on_next(430, 2),
# on_next(450, 9),
# on_next(520, 11),
# on_next(560, 20), on_error(600, ex))
#     results = scheduler.start(create)
#         return xs.publish(function (_xs) {
#             return _xs.zip(_xs.skip(1), function (prev, cur) {
#                 return cur + prev



#     results.messages.assert_equal(on_next(280, 7),
# on_next(290, 5),
# on_next(340, 9),
# on_next(360, 13),
# on_next(370, 11),
# on_next(390, 13),
# on_next(410, 20),
# on_next(430, 15),
# on_next(450, 11),
# on_next(520, 20),
# on_next(560, 31), on_error(600, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 600))


# test('PublishLambda_Zip_Dispose(self):
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 7),
# on_next(220, 3),
# on_next(280, 4),
# on_next(290, 1),
# on_next(340, 8),
# on_next(360, 5),
# on_next(370, 6),
# on_next(390, 7),
# on_next(410, 13),
# on_next(430, 2),
# on_next(450, 9),
# on_next(520, 11),
# on_next(560, 20), on_completed(600))
#     results = scheduler.startWithDispose(function () {
#         return xs.publish(function (_xs) {
#             return _xs.zip(_xs.skip(1), function (prev, cur) {
#                 return cur + prev


#     }, 470)
#     results.messages.assert_equal(on_next(280, 7),
# on_next(290, 5),
# on_next(340, 9),
# on_next(360, 13),
# on_next(370, 11),
# on_next(390, 13),
# on_next(410, 20),
# on_next(430, 15),
# on_next(450, 11))
#     xs.subscriptions.assert_equal(subscribe(200, 470))
