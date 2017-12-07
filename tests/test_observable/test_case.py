import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestCase(unittest.TestCase):
    def test_case_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(270, 3), close(300))
        ys = scheduler.create_hot_observable(send(220, 11), send(250, 12), send(280, 13), close(310))
        zs = scheduler.create_hot_observable(send(230, 21), send(240, 22), send(290, 23), close(320))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 1, map, zs)
        results = scheduler.start(create)

        results.messages.assert_equal(send(210, 1), send(240, 2), send(270, 3), close(300))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        ys.subscriptions.assert_equal()
        zs.subscriptions.assert_equal()

    def test_case_two(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(270, 3), close(300))
        ys = scheduler.create_hot_observable(send(220, 11), send(250, 12), send(280, 13), close(310))
        zs = scheduler.create_hot_observable(send(230, 21), send(240, 22), send(290, 23), close(320))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 2, map, zs)
        results = scheduler.start(create)

        results.messages.assert_equal(send(220, 11), send(250, 12), send(280, 13), close(310))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal()

    def test_case_three(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(270, 3), close(300))
        ys = scheduler.create_hot_observable(send(220, 11), send(250, 12), send(280, 13), close(310))
        zs = scheduler.create_hot_observable(send(230, 21), send(240, 22), send(290, 23), close(320))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 3, map, zs)
        results = scheduler.start(create)

        results.messages.assert_equal(send(230, 21), send(240, 22), send(290, 23), close(320))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal()
        zs.subscriptions.assert_equal(subscribe(200, 320))

    def test_case_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(270, 3), close(300))
        ys = scheduler.create_hot_observable(send(220, 11), send(250, 12), send(280, 13), close(310))
        zs = scheduler.create_hot_observable(send(230, 21), send(240, 22), send(290, 23), close(320))
        map = {
            1: xs,
            2: ys
        }
        def create():
            def selector():
                raise Exception(ex)
            return Observable.switch_case(selector, map, zs)
        results = scheduler.start(create)

        results.messages.assert_equal(throw(200, ex))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal()
        zs.subscriptions.assert_equal()

    def test_case_with_default_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(270, 3), close(300))
        ys = scheduler.create_hot_observable(send(220, 11), send(250, 12), send(280, 13), close(310))
        map = {
            1: xs,
            2: ys
        }

        def create():
            return Observable.switch_case(lambda: 1, map, scheduler=scheduler)
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(210, 1), send(240, 2), send(270, 3), close(300))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        ys.subscriptions.assert_equal()

    def test_case_with_default_two(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(270, 3), close(300))
        ys = scheduler.create_hot_observable(send(220, 11), send(250, 12), send(280, 13), close(310))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 2, map, scheduler=scheduler)
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(220, 11), send(250, 12), send(280, 13), close(310))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_case_with_default_three(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(270, 3), close(300))
        ys = scheduler.create_hot_observable(send(220, 11), send(250, 12), send(280, 13), close(310))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 3, map, scheduler=scheduler)
        results = scheduler.start(create=create)

        results.messages.assert_equal(close(201))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal()

    def test_case_with_default_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(270, 3), close(300))
        ys = scheduler.create_hot_observable(send(220, 11), send(250, 12), send(280, 13), close(310))
        map = {
            1: xs,
            2: ys
        }
        def create():
            def selector():
                raise Exception(ex)
            return Observable.switch_case(selector, map, scheduler=scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(throw(200, ex))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal()
