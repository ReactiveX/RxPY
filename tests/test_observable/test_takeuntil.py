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


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestTakeUntil(unittest.TestCase):

    def test_take_until_preempt_somedata_next(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        r_msgs = [on_next(150, 1), on_next(225, 99), on_completed(230)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_completed(225))

    def test_take_until_preempt_somedata_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        r_msgs = [on_next(150, 1), on_error(225, ex)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.take_until(r)
        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_error(225, ex))

    def test_take_until_nopreempt_somedata_empty(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        r_msgs = [on_next(150, 1), on_completed(225)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

    def test_take_until_nopreempt_somedata_never(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
        l = scheduler.create_hot_observable(l_msgs)
        r = Observable.never()

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

    def test_take_until_preempt_never_next(self):
        scheduler = TestScheduler()
        r_msgs = [on_next(150, 1), on_next(225, 2), on_completed(250)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(225))

    def test_take_until_preempt_never_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        r_msgs = [on_next(150, 1), on_error(225, ex)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(225, ex))

    def test_take_until_nopreempt_never_empty(self):
        scheduler = TestScheduler()
        r_msgs = [on_next(150, 1), on_completed(225)]
        l = Observable.never()
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_take_until_nopreempt_never_never(self):
        scheduler = TestScheduler()
        l = Observable.never()
        r = Observable.never()

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal()

    def test_take_until_preempt_beforefirstproduced(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
        r_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
        l = scheduler.create_hot_observable(l_msgs)
        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_completed(210))

    def test_take_until_preempt_beforefirstproduced_remain_silent_and_proper_disposed(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_error(215, 'ex'), on_completed(240)]
        r_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
        source_not_disposed = [False]

        def action():
            source_not_disposed[0] = True
        l = scheduler.create_hot_observable(l_msgs).do_action(on_next=action)

        r = scheduler.create_hot_observable(r_msgs)

        def create():
            return l.take_until(r)

        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(210))
        assert(not source_not_disposed[0])

    def test_take_until_nopreempt_afterlastproduced_proper_disposed_signal(self):
        scheduler = TestScheduler()
        l_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
        r_msgs = [on_next(150, 1), on_next(250, 2), on_completed(260)]
        signal_not_disposed = [False]
        l = scheduler.create_hot_observable(l_msgs)

        def action():
            signal_not_disposed[0] = True
        r = scheduler.create_hot_observable(r_msgs).do_action(on_next=action)

        def create():
            return l.take_until(r)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(230, 2), on_completed(240))
        assert(not signal_not_disposed[0])

