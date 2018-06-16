import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestManySelect(unittest.TestCase):

    def test_many_select_law_1(self):
        xs = Observable.range(1, 0)

        left = xs.many_select(lambda x: x.first())
        right = xs

        left.sequence_equal(right).first().subscribe_(self.assertTrue)

    def test_many_select_basic(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(220, 2),
            on_next(270, 3),
            on_next(410, 4),
            on_completed(500)
        )

        def create():
            return xs.many_select(lambda ys: ys.first()).merge_all()

        res = scheduler.start(create)

        assert res.messages == [
            on_next(220, 2),
            on_next(270, 3),
            on_next(410, 4),
            on_completed(500)]

        assert xs.subscriptions == [
            subscribe(200, 500)]

    def test_many_select_error(self):
        scheduler = TestScheduler()

        ex = Exception()

        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(220, 2),
            on_next(270, 3),
            on_next(410, 4),
            on_error(500, ex)
        )

        def create():
            return xs.many_select(lambda ys: ys.first()).merge_all()

        res = scheduler.start(create)

        assert res.messages == [
            on_next(220, 2),
            on_next(270, 3),
            on_next(410, 4),
            on_error(500, ex)]

        assert xs.subscriptions == [
            subscribe(200, 500)]
