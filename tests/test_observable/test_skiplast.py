import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSkipLast(unittest.TestCase):
    def test_skip_last_zero_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.skip_last(0)

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_skip_last_zero_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))

        def create():
            return xs.skip_last(0)

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_skip_last_zero_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))

        def create():
            return xs.skip_last(0)

        results = scheduler.start(create)

        results.messages.assert_equal(send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_skip_last_one_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.skip_last(1)

        results = scheduler.start(create)

        results.messages.assert_equal(send(250, 2), send(270, 3), send(310, 4), send(360, 5), send(380, 6), send(410, 7), send(590, 8), close(650))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_skip_last_one_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))

        def create():
            return xs.skip_last(1)

        results = scheduler.start(create)

        results.messages.assert_equal(send(250, 2), send(270, 3), send(310, 4), send(360, 5), send(380, 6), send(410, 7), send(590, 8), throw(650, ex))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_skip_last_one_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))

        def create():
            return xs.skip_last(1)

        results = scheduler.start(create)

        results.messages.assert_equal(send(250, 2), send(270, 3), send(310, 4), send(360, 5), send(380, 6), send(410, 7), send(590, 8))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_skip_last_three_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), close(650))

        def create():
            return xs.skip_last(3)

        results = scheduler.start(create)

        results.messages.assert_equal(send(310, 2), send(360, 3), send(380, 4), send(410, 5), send(590, 6), close(650))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_skip_last_three_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9), throw(650, ex))

        def create():
            return xs.skip_last(3)

        results = scheduler.start(create)

        results.messages.assert_equal(send(310, 2), send(360, 3), send(380, 4), send(410, 5), send(590, 6), throw(650, ex))
        xs.subscriptions.assert_equal(subscribe(200, 650))

    def test_skip_last_three_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(250, 3), send(270, 4), send(310, 5), send(360, 6), send(380, 7), send(410, 8), send(590, 9))

        def create():
            return xs.skip_last(3)

        results = scheduler.start(create)

        results.messages.assert_equal(send(310, 2), send(360, 3), send(380, 4), send(410, 5), send(590, 6))
        xs.subscriptions.assert_equal(subscribe(200, 1000))
