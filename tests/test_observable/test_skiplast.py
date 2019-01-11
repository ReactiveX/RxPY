import unittest

from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipLast(unittest.TestCase):
    def test_skip_last_zero_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9),
                on_completed(650))

        def create():
            return xs.pipe(ops.skip_last(0))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(210, 2), on_next(250, 3), on_next(270, 4),
                on_next(310, 5), on_next(360, 6), on_next(380, 7),
                on_next(410, 8), on_next(590, 9), on_completed(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_skip_last_zero_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9),
                on_error(650, ex))

        def create():
            return xs.pipe(ops.skip_last(0))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(210, 2), on_next(250, 3), on_next(270, 4),
                on_next(310, 5), on_next(360, 6), on_next(380, 7),
                on_next(410, 8), on_next(590, 9), on_error(650, ex)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_skip_last_zero_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9))

        def create():
            return xs.pipe(ops.skip_last(0))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(210, 2), on_next(250, 3), on_next(270, 4),
                on_next(310, 5), on_next(360, 6), on_next(380, 7),
                on_next(410, 8), on_next(590, 9)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_skip_last_one_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9),
                on_completed(650))

        def create():
            return xs.pipe(ops.skip_last(1))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(250, 2), on_next(270, 3), on_next(310, 4),
                on_next(360, 5), on_next(380, 6), on_next(410, 7),
                on_next(590, 8), on_completed(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_skip_last_one_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9),
                on_error(650, ex))

        def create():
            return xs.pipe(ops.skip_last(1))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(250, 2), on_next(270, 3), on_next(310, 4),
                on_next(360, 5), on_next(380, 6), on_next(410, 7),
                on_next(590, 8), on_error(650, ex)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_skip_last_one_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9))

        def create():
            return xs.pipe(ops.skip_last(1))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(250, 2), on_next(270, 3), on_next(310, 4),
                on_next(360, 5), on_next(380, 6), on_next(410, 7),
                on_next(590, 8)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_skip_last_three_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9),
                on_completed(650))

        def create():
            return xs.pipe(ops.skip_last(3))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(310, 2), on_next(360, 3), on_next(380, 4),
                on_next(410, 5), on_next(590, 6), on_completed(650)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_skip_last_three_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9),
                on_error(650, ex))

        def create():
            return xs.pipe(ops.skip_last(3))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(310, 2), on_next(360, 3), on_next(380, 4),
                on_next(410, 5), on_next(590, 6), on_error(650, ex)]
        assert xs.subscriptions == [subscribe(200, 650)]

    def test_skip_last_three_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
                on_next(180, 1), on_next(210, 2), on_next(250, 3),
                on_next(270, 4), on_next(310, 5), on_next(360, 6),
                on_next(380, 7), on_next(410, 8), on_next(590, 9))

        def create():
            return xs.pipe(ops.skip_last(3))

        results = scheduler.start(create)

        assert results.messages == [
                on_next(310, 2), on_next(360, 3), on_next(380, 4),
                on_next(410, 5), on_next(590, 6)]
        assert xs.subscriptions == [subscribe(200, 1000)]
