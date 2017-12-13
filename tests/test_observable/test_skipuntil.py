import unittest

from rx import Observable
from rx import AnonymousObservable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipUntil(unittest.TestCase):

    def test_skip_until_somedata_next(self):
        scheduler = TestScheduler()
        l_msgs = [send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250)]
        r_msgs = [send(150, 1), send(225, 99), close(230)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        assert results.messages == [send(230, 4), send(240, 5), close(250)]

    def test_skip_until_somedata_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        l_msgs = [send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250)]
        r_msgs = [send(150, 1), throw(225, ex)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)
        results = scheduler.start(create)

        assert results.messages == [throw(225, ex)]

    def test_skip_until_somedata_empty(self):
        scheduler = TestScheduler()
        l_msgs = [send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250)]
        r_msgs = [send(150, 1), close(225)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        assert results.messages == []

    def test_skip_until_never_next(self):
        scheduler = TestScheduler()
        r_msgs = [send(150, 1), send(225, 2), close(250)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        assert results.messages == []

    def test_skip_until_never_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        r_msgs = [send(150, 1), throw(225, ex)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        assert results.messages == [throw(225, ex)]

    def test_skip_until_somedata_never(self):
        scheduler = TestScheduler()
        l_msgs = [send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250)]
        l = scheduler.create_hot_observable(l_msgs)
        r = Observable.never()

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        assert results.messages == []

    def test_skip_until_never_empty(self):
        scheduler = TestScheduler()
        r_msgs = [send(150, 1), close(225)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        assert results.messages == []

    def test_skip_until_never_never(self):
        scheduler = TestScheduler()
        l = Observable.never()
        r = Observable.never()

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        assert results.messages == []

    def test_skip_until_has_completed_causes_disposal(self):
        scheduler = TestScheduler()
        l_msgs = [send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250)]
        disposed = [False]
        l = scheduler.create_hot_observable(l_msgs)

        def subscribe(observer, scheduler=None):
            disposed[0] = True

        r = AnonymousObservable(subscribe)

        def create():
            return l.skip_until(r)

        results = scheduler.start(create)
        assert results.messages == []
        assert(disposed[0])
