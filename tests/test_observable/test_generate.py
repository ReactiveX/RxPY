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
                lambda x: x)

        results = scheduler.start(create)

        assert results.messages == [
                            send(200, 0),
                            send(200, 1),
                            send(200, 2),
                            send(200, 3),
                            close(200)]

    def test_generate_throw_condition(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return Observable.generate(0,
                lambda x: _raise('ex'),
                lambda x: x + 1,
                lambda x: x)
        results = scheduler.start(create)

        assert results.messages == [throw(200, ex)]

    def test_generate_throw_result_selector(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return Observable.generate(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: _raise('ex'))

        results = scheduler.start(create)
        assert results.messages == [throw(200, ex)]

    def test_generate_throw_iterate(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return Observable.generate(0,
                lambda x: True,
                lambda x: _raise(ex),
                lambda x: x)
        results = scheduler.start(create)

        assert results.messages == [
                            send(200, 0),
                            throw(200, ex)]

    def test_generate_dispose(self):
        scheduler = TestScheduler()
        ex = 'ex'

        def create():
            return Observable.generate(0,
                lambda x: True,
                lambda x: x + 1,
                lambda x: x)

        results = scheduler.start(create, disposed=200)
        assert results.messages == []

    def test_generate_repeat(self):
        scheduler = TestScheduler()

        def create():
            return Observable.generate(0,
                    lambda x: x <= 3,
                    lambda x: x + 1,
                    lambda x: x) \
                .repeat(2)

        results = scheduler.start(create)

        assert results.messages == [
                send(200, 0),
                send(200, 1),
                send(200, 2),
                send(200, 3),
                send(200, 0),
                send(200, 1),
                send(200, 2),
                send(200, 3),
                close(200)]
