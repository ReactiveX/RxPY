import unittest

from rx import Observable
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


class TestGenerateWithRelativeTime(unittest.TestCase):
    def test_generate_timespan_finite(self):
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: x <= 3,
                lambda x: x + 1,
                lambda x: x,
                lambda x: x + 1,
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2), on_next(211, 3), on_completed(211))

    def test_generate_timespan_throw_condition(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: _raise(ex),
                lambda x: x + 1,
                lambda x: x,
                lambda x: x + 1,
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(201, ex))

    def test_generate_timespan_throw_result_selector(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: _raise(ex),
                lambda x: x + 1,
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(201, ex))

    def test_generate_timespan_throw_iterate(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: _raise(ex),
                lambda x: x,
                lambda x: x + 1,
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(202, 0), on_error(202, ex))

    def test_generate_timespan_throw_timeselector(self):
        ex = 'ex'
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: _raise(ex),
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(201, ex))

    def test_generate_timespan_dispose(self):
        scheduler = TestScheduler()

        def create():
            return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: x + 1,
                scheduler=scheduler)

        results = scheduler.start(create, disposed=210)
        results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2))

    def test_generate_datetime_offset_finite(self):
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: scheduler.now() + x + 1,
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2), on_next(211, 3), on_completed(211))

    def test_generate_datetime_offset_throw_condition(self):
        ex = 'ex'
        scheduler = TestScheduler()
        return Observable.generate_with_relative_time(0,
                lambda x: _raise(ex),
                lambda x: x + 1,
                lambda x: x,
                lambda x: scheduler.now() + x + 1,
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(201, ex))

    def test_generate_datetime_offset_throw_result_selector(self):
        ex = 'ex'
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: _raise(ex),
                lambda x: scheduler.now() + x + 1,
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(201, ex))

    def test_generate_datetime_offset_throw_iterate(self):
        ex = 'ex'
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: _raise(ex),
                lambda x: x,
                lambda x: scheduler.now() + x + 1,
                scheduler=scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_next(202, 0), on_error(202, ex))

    def test_generate_datetime_offset_throw_time_selector(self):
        ex = 'ex'
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: _raise(ex),
                scheduler=scheduler)

        results.messages.assert_equal(on_error(201, ex))

    def test_generate_datetime_offset_dispose(self):
        scheduler = TestScheduler()

        return Observable.generate_with_relative_time(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                lambda x: scheduler.now() + x + 1,
                scheduler=scheduler)

        results = scheduler.start(create, disposed=210)
        results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2))

