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


class TestGenerate(unittest.TestCase):
    def test_generate_finite(self):
        scheduler = TestScheduler()

        def create():
            return Observable.generate(0,
                lambda x: x <= 3,
                lambda x: x + 1,
                lambda x: x,
                scheduler)

        results = scheduler.start(create)

        results.messages.assert_equal(
                            on_next(201, 0),
                            on_next(202, 1),
                            on_next(203, 2),
                            on_next(204, 3),
                            on_completed(205)
                        )

    def test_generate_throw_condition(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return Observable.generate(0,
                lambda x: _raise('ex'),
                lambda x: x + 1,
                lambda x: x,
                scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(201, ex))

    def test_generate_throw_result_selector(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return Observable.generate(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: _raise('ex'),
                scheduler)

        results = scheduler.start(create)
        results.messages.assert_equal(on_error(201, ex))

    def test_generate_throw_iterate(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return Observable.generate(0,
                lambda x: True,
                lambda x: _raise(ex),
                lambda x: x,
                scheduler)
        results = scheduler.start(create)

        results.messages.assert_equal(
                            on_next(201, 0),
                            on_error(202, ex)
                        )

    def test_generate_dispose(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return Observable.generate(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x,
                scheduler)

        results = scheduler.start(create, disposed=203)
        results.messages.assert_equal(
                            on_next(201, 0),
                            on_next(202, 1))

    def test_generate_repeat(self):
        scheduler = TestScheduler()

        def create():
            return Observable.generate(0,
                    lambda x: x <= 3,
                    lambda x: x + 1,
                    lambda x: x,
                    scheduler) \
                .repeat(2)

        results = scheduler.start(create)

        results.messages.assert_equal(
                on_next(201, 0),
                on_next(202, 1),
                on_next(203, 2),
                on_next(204, 3),
                on_next(206, 0),
                on_next(207, 1),
                on_next(208, 2),
                on_next(209, 3),
                on_completed(210)
        )
