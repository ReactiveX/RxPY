import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestCase(unittest.TestCase):
    def test_case_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        zs = scheduler.create_hot_observable(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 1, map, zs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        ys.subscriptions.assert_equal()
        zs.subscriptions.assert_equal()

    def test_case_two(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        zs = scheduler.create_hot_observable(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 2, map, zs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal(subscribe(200, 310))
        zs.subscriptions.assert_equal()

    def test_case_three(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        zs = scheduler.create_hot_observable(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 3, map, zs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal()
        zs.subscriptions.assert_equal(subscribe(200, 320))

    def test_case_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        zs = scheduler.create_hot_observable(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
        map = {
            1: xs,
            2: ys
        }
        def create():
            def selector():
                raise Exception(ex)
            return Observable.switch_case(selector, map, zs)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(200, ex))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal()
        zs.subscriptions.assert_equal()

    def test_case_with_default_one(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        map = {
            1: xs,
            2: ys
        }

        def create():
            return Observable.switch_case(lambda: 1, map, scheduler=scheduler)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        ys.subscriptions.assert_equal()

    def test_case_with_default_two(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 2, map, scheduler=scheduler)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal(subscribe(200, 310))

    def test_case_with_default_three(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        map = {
            1: xs,
            2: ys
        }
        def create():
            return Observable.switch_case(lambda: 3, map, scheduler=scheduler)
        results = scheduler.start(create=create)

        results.messages.assert_equal(on_completed(201))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal()

    def test_case_with_default_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
        ys = scheduler.create_hot_observable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
        map = {
            1: xs,
            2: ys
        }
        def create():
            def selector():
                raise Exception(ex)
            return Observable.switch_case(selector, map, scheduler=scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(200, ex))
        xs.subscriptions.assert_equal()
        ys.subscriptions.assert_equal()
