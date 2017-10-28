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


def _extract(x):
    return x.first()


def _duplicate(x):
    """This is ``pure`` or ``return``. We need it in order to compare equality
    of inputs and outputs of ``many_select``, since we don't have a true
    ``extract`` function.
    """
    return Observable.from_iterable([x]).first()


def _comparer(x, y):
    """Compares two items of type ``Observable[a]``."""
    return x.sequence_equal(y).first()


class TestManySelect(unittest.TestCase):

    def _obs_equal(self, left, right):
        return left.sequence_equal(right, _comparer).first().subscribe(self.assertTrue)

    def test_many_select_law_1(self):
        xs = Observable.range(1, 3)

        left = xs.many_select(_extract)
        right = xs.map(_duplicate)  # since .first() returns ``Observable[a]`` and not ``a``.

        self._obs_equal(left, right)

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
            return xs.many_select(lambda ys: ys.first(), scheduler).merge_all()

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(221, 2),
            on_next(271, 3),
            on_next(411, 4),
            on_completed(501)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 500)
        )

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
            return xs.many_select(lambda ys: ys.first(), scheduler).merge_all()

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(221, 2),
            on_next(271, 3),
            on_next(411, 4),
            on_error(501, ex)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 500)
        )
