import unittest
from datetime import datetime

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestTimeout(unittest.TestCase):
    def test_timeout_in_time(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))

        def create():
            return xs.timeout(500, None, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))

    def test_timeout_out_of_time(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))

        def create():
            return xs.timeout(205, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(210, 2), on_next(230, 3), on_next(260, 4), on_next(300, 5), on_next(350, 6), on_completed(400))

    def test_timeout_timeout_occurs_1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(70, 1), on_next(130, 2), on_next(310, 3), on_next(400, 4), on_completed(500))
        ys = scheduler.create_cold_observable(on_next(50, -1), on_next(200, -2), on_next(310, -3), on_completed(320))

        def create():
            return xs.timeout(100, ys, scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(350, -1), on_next(500, -2), on_next(610, -3), on_completed(620))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        ys.subscriptions.assert_equal(subscribe(300, 620))

    def test_timeout_timeout_occurs_2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(70, 1), on_next(130, 2), on_next(240, 3), on_next(310, 4), on_next(430, 5), on_completed(500))
        ys = scheduler.create_cold_observable(on_next(50, -1), on_next(200, -2), on_next(310, -3), on_completed(320))

        def create():
            return xs.timeout(100, ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(240, 3), on_next(310, 4), on_next(460, -1), on_next(610, -2), on_next(720, -3), on_completed(730))
        xs.subscriptions.assert_equal(subscribe(200, 410))
        ys.subscriptions.assert_equal(subscribe(410, 730))

    def test_timeout_timeout_occurs_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(70, 1), on_next(130, 2), on_next(240, 3), on_next(310, 4), on_next(430, 5), on_completed(500))
        ys = scheduler.create_cold_observable()

        def create():
            return xs.timeout(100, ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(240, 3), on_next(310, 4))
        xs.subscriptions.assert_equal(subscribe(200, 410))
        ys.subscriptions.assert_equal(subscribe(410, 1000))

    def test_timeout_timeout_occurs_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(500))
        ys = scheduler.create_cold_observable(on_next(100, -1))

        def create():
            return xs.timeout(100, ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(400, -1))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        ys.subscriptions.assert_equal(subscribe(300, 1000))

    def test_timeout_timeout_occurs_error(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_error(500, 'ex'))
        ys = scheduler.create_cold_observable(on_next(100, -1))

        def create():
            return xs.timeout(100, ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(400, -1))
        xs.subscriptions.assert_equal(subscribe(200, 300))
        ys.subscriptions.assert_equal(subscribe(300, 1000))

    def test_timeout_timeout_not_occurs_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(250))
        ys = scheduler.create_cold_observable(on_next(100, -1))

        def create():
            return xs.timeout(100, ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(250))
        xs.subscriptions.assert_equal(subscribe(200, 250))
        ys.subscriptions.assert_equal()

    def test_timeout_timeout_not_occurs_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_error(250, ex))
        ys = scheduler.create_cold_observable(on_next(100, -1))

        def create():
            return xs.timeout(100, ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_error(250, ex))
        xs.subscriptions.assert_equal(subscribe(200, 250))
        ys.subscriptions.assert_equal()

    def test_timeout_timeout_does_not_occur(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(70, 1), on_next(130, 2), on_next(240, 3), on_next(320, 4), on_next(410, 5), on_completed(500))
        ys = scheduler.create_cold_observable(on_next(50, -1), on_next(200, -2), on_next(310, -3), on_completed(320))

        def create():
            return xs.timeout(100, ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(240, 3), on_next(320, 4), on_next(410, 5), on_completed(500))
        xs.subscriptions.assert_equal(subscribe(200, 500))
        ys.subscriptions.assert_equal()

    def test_timeout_datetime_offset_timeout_occurs(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(410, 1))
        ys = scheduler.create_cold_observable(on_next(100, -1))

        def create():
            return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(500, -1))
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(400, 1000))

    def test_timeout_datetime_offset_timeout_does_not_occur_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_completed(390))
        ys = scheduler.create_cold_observable(on_next(100, -1))

        def create():
            return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler=scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(310, 1), on_completed(390))
        xs.subscriptions.assert_equal(subscribe(200, 390))
        ys.subscriptions.assert_equal()

    def test_timeout_datetime_offset_timeout_does_not_occur_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_error(390, ex))
        ys = scheduler.create_cold_observable(on_next(100, -1))

        def create():
            return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(310, 1), on_error(390, ex))
        xs.subscriptions.assert_equal(subscribe(200, 390))
        ys.subscriptions.assert_equal()

    def test_timeout_datetime_offset_timeout_occur_2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable(on_next(100, -1))

        def create():
            return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler=scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(310, 1), on_next(350, 2), on_next(500, -1))
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(400, 1000))

    def test_timeout_datetime_offset_timeout_occur_3(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(310, 1), on_next(350, 2), on_next(420, 3), on_completed(450))
        ys = scheduler.create_cold_observable()

        def create():
            return xs.timeout(datetime.fromtimestamp(400/1000.0), ys, scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(on_next(310, 1), on_next(350, 2))
        xs.subscriptions.assert_equal(subscribe(200, 400))
        ys.subscriptions.assert_equal(subscribe(400, 1000))
