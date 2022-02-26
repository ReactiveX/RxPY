import unittest

import rx
from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestAmb(unittest.TestCase):

    def test_amb_never2(self):
        scheduler = TestScheduler()
        l = rx.never()
        r = rx.never()

        def create():
            return l.pipe(ops.amb(r))

        results = scheduler.start(create)
        assert results.messages == []

    def test_amb_never3(self):
        scheduler = TestScheduler()
        n1 = rx.never()
        n2 = rx.never()
        n3 = rx.never()

        def create():
            return rx.amb(n1, n2, n3)

        results = scheduler.start(create)
        assert results.messages == []

    def test_amb_never_empty(self):
        scheduler = TestScheduler()
        r_msgs = [on_next(150, 1), on_completed(225)]
        n = rx.never()
        e = scheduler.create_hot_observable(r_msgs)

        def create():
            return n.pipe(ops.amb(e))

        results = scheduler.start(create)
        assert results.messages == [on_completed(225)]

    def test_amb_empty_never(self):
        scheduler = TestScheduler()
        r_msgs = [on_next(150, 1), on_completed(225)]
        n = rx.never()
        e = scheduler.create_hot_observable(r_msgs)

        def create():
            return e.pipe(ops.amb(n))

        results = scheduler.start(create)
        assert results.messages == [on_completed(225)]

    def test_amb_regular_should_dispose_loser(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(240)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
        source_not_disposed = [False]
        o1 = scheduler.create_hot_observable(msgs1)

        def action():
            source_not_disposed[0] = True

        o2 = scheduler.create_hot_observable(msgs2).pipe(
                ops.do_action(on_next=action),
                )

        def create():
            return o1.pipe(ops.amb(o2))
        results = scheduler.start(create)

        assert results.messages == [on_next(210, 2), on_completed(240)]
        assert(not source_not_disposed[0])

    def test_amb_winner_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
        source_not_disposed = [False]
        o1 = scheduler.create_hot_observable(msgs1)

        def action():
            source_not_disposed[0] = True

        o2 = scheduler.create_hot_observable(msgs2).pipe(
                ops.do_action(on_next=action),
                )

        def create():
            return o1.pipe(ops.amb(o2))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_error(220, ex)]
        assert(not source_not_disposed[0])

    def test_amb_loser_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(220, 2), on_error(230, ex)]
        msgs2 = [on_next(150, 1), on_next(210, 3), on_completed(250)]
        source_not_disposed = [False]

        def action():
            source_not_disposed[0] = True
        o1 = scheduler.create_hot_observable(msgs1).pipe(
                ops.do_action(on_next=action),
                )

        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.pipe(ops.amb(o2))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 3), on_completed(250)]
        assert(not source_not_disposed[0])

    def test_amb_throws_before_election(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(210, ex)]
        msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
        source_not_disposed = [False]
        o1 = scheduler.create_hot_observable(msgs1)

        def action():
            source_not_disposed[0] = True

        o2 = scheduler.create_hot_observable(msgs2).pipe(
                ops.do_action(on_next=action),
                )

        def create():
            return o1.pipe(ops.amb(o2))

        results = scheduler.start(create)

        assert results.messages == [on_error(210, ex)]
        assert(not source_not_disposed[0])
