import unittest

from rx import Observable
from rx import AnonymousObservable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipUntil(unittest.TestCase):

    def test_skip_until_somedata_next(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        r_msgs = [on_next(150, 1), on_next(225, 99), on_completed(230)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(230, 4), on_next(240, 5), on_completed(250))

    def test_skip_until_somedata_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        r_msgs = [on_next(150, 1), on_error(225, ex)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(225, ex))

    def test_skip_until_somedata_empty(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        r_msgs = [on_next(150, 1), on_completed(225)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_skip_until_never_next(self):
        scheduler = TestScheduler()
        r_msgs = [on_next(150, 1), on_next(225, 2), on_completed(250)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_skip_until_never_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        r_msgs = [on_next(150, 1), on_error(225, ex)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(225, ex))

    def test_skip_until_somedata_never(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        l = scheduler.create_hot_observable(l_msgs)
        r = Observable.never()

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_skip_until_never_empty(self):
        scheduler = TestScheduler()
        r_msgs = [on_next(150, 1), on_completed(225)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_skip_until_never_never(self):
        scheduler = TestScheduler()
        l = Observable.never()
        r = Observable.never()

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_skip_until_has_completed_causes_disposal(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        disposed = [False]
        l = scheduler.create_hot_observable(l_msgs)

        def subscribe(observer):
            disposed[0] = True

        r = AnonymousObservable(subscribe)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal()
        assert(disposed[0])
