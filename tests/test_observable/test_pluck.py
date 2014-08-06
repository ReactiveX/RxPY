import unittest

from rx.observable import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import Disposable, SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestPluck(unittest.TestCase):

    def test_pluck_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            on_next(180, {"prop": 1}),
            on_next(210, {"prop": 2}),
            on_next(240, {"prop": 3}),
            on_next(290, {"prop": 4}),
            on_next(350, {"prop": 5}),
            on_completed(400),
            on_next(410, {"prop": -1}),
            on_completed(420),
            on_error(430, Exception('ex'))
        )
        results = scheduler.start(create=lambda: xs.pluck('prop'))

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(240, 3),
            on_next(290, 4),
            on_next(350, 5),
            on_completed(400)
        )
        xs.subscriptions.assert_equal(subscribe(200, 400))
