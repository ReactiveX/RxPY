import unittest

from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler, is_prime

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipWhile(unittest.TestCase):
    def test_skip_while_complete_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(90, -1), on_next(110, -1), on_next(210, 2),
            on_next(260, 5), on_next(290, 13), on_next(320, 3),
            on_completed(330), on_next(350, 7), on_next(390, 4),
            on_next(410, 17), on_next(450, 8), on_next(500, 23),
            on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(ops.skip_while(predicate))
        results = scheduler.start(create)

        assert results.messages == [on_completed(330)]
        assert xs.subscriptions == [subscribe(200, 330)]
        assert(invoked[0] == 4)

    def test_skip_while_complete_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(90, -1), on_next(110, -1), on_next(210, 2),
                on_next(260, 5), on_next(290, 13), on_next(320, 3),
                on_next(350, 7), on_next(390, 4), on_next(410, 17),
                on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(ops.skip_while(predicate))
        results = scheduler.start(create)

        assert results.messages == [on_next(390, 4), on_next(
            410, 17), on_next(450, 8), on_next(500, 23), on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 6)

    def test_skip_while_error_before(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(90, -1), on_next(110, -1), on_next(210, 2),
                on_next(260, 5), on_error(270, ex), on_next(290, 13),
                on_next(320, 3), on_next(350, 7), on_next(390, 4),
                on_next(410, 17), on_next(450, 8), on_next(500, 23),
                on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(ops.skip_while(predicate))
        results = scheduler.start(create)

        assert results.messages == [on_error(270, ex)]
        assert xs.subscriptions == [subscribe(200, 270)]
        assert(invoked[0] == 2)

    def test_skip_while_error_after(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(90, -1), on_next(110, -1), on_next(210, 2),
                on_next(260, 5), on_next(290, 13), on_next(320, 3),
                on_next(350, 7), on_next(390, 4), on_next(410, 17),
                on_next(450, 8), on_next(500, 23), on_error(600, ex))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(ops.skip_while(predicate))
        results = scheduler.start(create)

        assert results.messages == [on_next(390, 4), on_next(
            410, 17), on_next(450, 8), on_next(500, 23), on_error(600, ex)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 6)

    def test_skip_while_dispose_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(90, -1), on_next(110, -1), on_next(210, 2),
                on_next(260, 5), on_next(290, 13), on_next(320, 3),
                on_next(350, 7), on_next(390, 4), on_next(410, 17),
                on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(ops.skip_while(predicate))
        results = scheduler.start(create, disposed=300)

        assert results.messages == []
        assert xs.subscriptions == [subscribe(200, 300)]
        assert(invoked[0] == 3)

    def test_skip_while_dispose_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(90, -1), on_next(110, -1), on_next(210, 2),
                on_next(260, 5), on_next(290, 13), on_next(320, 3),
                on_next(350, 7), on_next(390, 4), on_next(410, 17),
                on_next(450, 8), on_next(500, 23), on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(ops.skip_while(predicate))
        results = scheduler.start(create, disposed=470)

        assert results.messages == [on_next(390, 4), on_next(410, 17), on_next(450, 8)]
        assert xs.subscriptions == [subscribe(200, 470)]
        assert(invoked[0] == 6)

    def test_skip_while_zero(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(90, -1), on_next(110, -1), on_next(205, 100),
                on_next(210, 2), on_next(260, 5), on_next(290, 13),
                on_next(320, 3), on_next(350, 7), on_next(390, 4),
                on_next(410, 17), on_next(450, 8), on_next(500, 23),
                on_completed(600))
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                return is_prime(x)
            return xs.pipe(ops.skip_while(predicate))
        results = scheduler.start(create)

        assert results.messages == [
                on_next(205, 100), on_next(210, 2), on_next(260, 5),
                on_next(290, 13), on_next(320, 3), on_next(350, 7),
                on_next(390, 4), on_next(410, 17), on_next(450, 8),
                on_next(500, 23), on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]
        assert(invoked[0] == 1)

    def test_skip_while_on_error(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(90, -1), on_next(110, -1), on_next(210, 2),
                on_next(260, 5), on_next(290, 13), on_next(320, 3),
                on_next(350, 7), on_next(390, 4), on_next(410, 17),
                on_next(450, 8), on_next(500, 23), on_completed(600))
        ex = 'ex'
        invoked = [0]

        def create():
            def predicate(x):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)

                return is_prime(x)
            return xs.pipe(ops.skip_while(predicate))
        results = scheduler.start(create)

        assert results.messages == [on_error(290, ex)]
        assert xs.subscriptions == [subscribe(200, 290)]
        assert invoked[0] == 3

    def test_skip_while_index(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(90, -1), on_next(110, -1), on_next(210, 2),
            on_next(260, 5), on_next(290, 13), on_next(320, 3),
            on_next(350, 7), on_next(390, 4), on_next(410, 17),
            on_next(450, 8), on_next(500, 23),
            on_completed(600))

        def create():
            def predicate(x, i):
                return i < 5
            return xs.pipe(ops.skip_while_indexed(predicate))
        results = scheduler.start(create)

        assert results.messages == [
            on_next(390, 4),
            on_next(410, 17),
            on_next(450, 8),
            on_next(500, 23),
            on_completed(600)
        ]
        assert xs.subscriptions == [subscribe(200, 600)]
