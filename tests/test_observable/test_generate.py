import unittest

import rx
from rx import operators as ops
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
            return rx.generate(0,
                               lambda x: x <= 3,
                               lambda x: x + 1,
                               lambda x: x)

        results = scheduler.start(create)

        assert results.messages == [
            on_next(200, 0),
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_completed(200)]

    def test_generate_throw_condition(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return rx.generate(0,
                               lambda x: _raise('ex'),
                               lambda x: x + 1,
                               lambda x: x)
        results = scheduler.start(create)

        assert results.messages == [on_error(200, ex)]

    def test_generate_throw_result_mapper(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return rx.generate(0,
                               lambda x: True,
                               lambda x: x + 1,
                               lambda x: _raise('ex'))

        results = scheduler.start(create)
        assert results.messages == [on_error(200, ex)]

    def test_generate_throw_iterate(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return rx.generate(0,
                               lambda x: True,
                               lambda x: _raise(ex),
                               lambda x: x)
        results = scheduler.start(create)

        assert results.messages == [
            on_next(200, 0),
            on_error(200, ex)]

    def test_generate_dispose(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return rx.generate(0,
                               lambda x: True,
                               lambda x: x + 1,
                               lambda x: x)

        results = scheduler.start(create, disposed=200)
        assert results.messages == []

    def test_generate_repeat(self):
        scheduler = TestScheduler()

        def create():
            return rx.generate(0,
                               lambda x: x <= 3,
                               lambda x: x + 1,
                               lambda x: x) \
                .pipe(ops.repeat(2))

        results = scheduler.start(create)

        assert results.messages == [
            on_next(200, 0),
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_next(200, 0),
            on_next(200, 1),
            on_next(200, 2),
            on_next(200, 3),
            on_completed(200)]
