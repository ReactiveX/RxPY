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
                            send(201, 0),
                            send(202, 1),
                            send(203, 2),
                            send(204, 3),
                            close(205)
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

        results.messages.assert_equal(throw(201, ex))

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
        results.messages.assert_equal(throw(201, ex))

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
                            send(201, 0),
                            throw(202, ex)
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
                            send(201, 0),
                            send(202, 1))

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
                send(201, 0),
                send(202, 1),
                send(203, 2),
                send(204, 3),
                send(206, 0),
                send(207, 1),
                send(208, 2),
                send(209, 3),
                close(210)
        )
