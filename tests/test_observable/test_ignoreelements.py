import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestIgnoreElements(unittest.TestCase):

    def test_ignore_values_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
        results = scheduler.start(create=lambda: xs.ignore_elements())

        results.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_ignore_values_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(610))
        results = scheduler.start(create=lambda: xs.ignore_elements())

        results.messages.assert_equal(on_completed(610))
        xs.subscriptions.assert_equal(subscribe(200, 610))

    def test_ignore_values_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(610, ex))
        results = scheduler.start(create=lambda: xs.ignore_elements())

        results.messages.assert_equal(on_error(610, ex))
        xs.subscriptions.assert_equal(subscribe(200, 610))
