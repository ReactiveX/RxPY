import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest


send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestGenerateWithRelativeTime(unittest.TestCase):
    def test_generate_timespan_finite(self):
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: x <= 3,
                lambda x: x + 1,
                lambda x: x,
                lambda x: x + 1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(201, 0), send(203, 1), send(206, 2), send(210, 3), close(210))

    def test_generate_timespan_throw_condition(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: _raise(ex),
                lambda x: x + 1,
                lambda x: x,
                lambda x: x + 1)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(200, ex))

    def test_generate_timespan_throw_result_selector(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: _raise(ex),
                lambda x: x + 1)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(200, ex))

    def test_generate_timespan_throw_iterate(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: _raise(ex),
                lambda x: x,
                lambda x: x + 1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(201, 0), throw(201, ex))

    def test_generate_timespan_throw_timeselector(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: _raise(ex))

        results = scheduler.start(create)
        results.messages.assert_equal(throw(200, ex))

    def test_generate_timespan_dispose(self):
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: x + 1)

        results = scheduler.start(create, disposed=210)
        results.messages.assert_equal(send(201, 0), send(203, 1), send(206, 2))

    def test_generate_datetime_offset_finite(self):
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: scheduler.now() + x + 1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(201, 0), send(203, 1), send(206, 2), send(210, 3), close(210))

    def test_generate_datetime_offset_throw_condition(self):
        ex = 'ex'
        scheduler = TestScheduler()
        return Observable.generate_with_relative_time(0,
                lambda x: _raise(ex),
                lambda x: x + 1,
                lambda x: x,
                lambda x: scheduler.now() + x + 1)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(200, ex))

    def test_generate_datetime_offset_throw_result_selector(self):
        ex = 'ex'
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: _raise(ex),
                lambda x: scheduler.now() + x + 1)

        results = scheduler.start(create)
        results.messages.assert_equal(throw(200, ex))

    def test_generate_datetime_offset_throw_iterate(self):
        ex = 'ex'
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: _raise(ex),
                lambda x: x,
                lambda x: scheduler.now() + x + 1)

        results = scheduler.start(create)
        results.messages.assert_equal(send(202, 0), throw(202, ex))

    def test_generate_datetime_offset_throw_time_selector(self):
        ex = 'ex'
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: _raise(ex))

        results.messages.assert_equal(throw(200, ex))

    def test_generate_datetime_offset_dispose(self):
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: scheduler.now() + x + 1)

        results = scheduler.start(create, disposed=210)
        results.messages.assert_equal(send(202, 0), send(204, 1), send(207, 2))

