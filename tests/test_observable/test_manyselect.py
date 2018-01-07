import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
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
            send(100, 1),
            send(220, 2),
            send(270, 3),
            send(410, 4),
            close(500)
        )

        def create():
            return xs.many_select(lambda ys: ys.first()).merge_all()

        res = scheduler.start(create)

        assert res.messages == [
            send(220, 2),
            send(270, 3),
            send(410, 4),
            close(500)]

        assert xs.subscriptions == [
            subscribe(200, 500)]

    def test_many_select_error(self):
        scheduler = TestScheduler()

        ex = Exception()

        xs = scheduler.create_hot_observable(
            send(100, 1),
            send(220, 2),
            send(270, 3),
            send(410, 4),
            throw(500, ex)
        )

        def create():
            return xs.many_select(lambda ys: ys.first()).merge_all()

        res = scheduler.start(create)

        assert res.messages == [
            send(220, 2),
            send(270, 3),
            send(410, 4),
            throw(500, ex)]

        assert xs.subscriptions == [
            subscribe(200, 500)]
