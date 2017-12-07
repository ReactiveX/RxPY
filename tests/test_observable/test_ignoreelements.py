import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestIgnoreElements(unittest.TestCase):

    def test_ignore_values_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))
        results = scheduler.start(create=lambda: xs.ignore_elements())

        results.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_ignore_values_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(610))
        results = scheduler.start(create=lambda: xs.ignore_elements())

        results.messages.assert_equal(close(610))
        xs.subscriptions.assert_equal(subscribe(200, 610))

    def test_ignore_values_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(610, ex))
        results = scheduler.start(create=lambda: xs.ignore_elements())

        results.messages.assert_equal(throw(610, ex))
        xs.subscriptions.assert_equal(subscribe(200, 610))
