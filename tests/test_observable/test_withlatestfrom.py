import unittest

from rx import Observable
from rx.core import Disposable
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import SerialDisposable

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

class TestWithLatestFrom(unittest.TestCase):

    def test_with_latest_from_never_never(self):
        scheduler = TestScheduler()
        e1 = Observable.never()
        e2 = Observable.never()

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_with_latest_from_never_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(210)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_with_latest_from_empty_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(210)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(210)]

    def test_with_latest_from_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), close(210)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(210)]

    def test_with_latest_from_empty_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(210)]

    def test_with_latest_from_return_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(220)]

    def test_with_latest_from_never_return(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = Observable.never()

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(220)]

    def test_with_latest_from_return_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(215, 2), close(210)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = Observable.never()

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_with_latest_from_return_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), send(220, 3), close(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(230)]

    def test_with_latest_from_empty_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_with_latest_from_error_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_with_latest_from_return_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_with_latest_from_throw_return(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_with_latest_from_throw_throw(self):
        ex1 = 'ex1'
        ex2 = 'ex2'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), throw(220, ex1)]
        msgs2 = [send(150, 1), throw(230, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex1)]

    def test_with_latest_from_error_throw(self):
        ex1 = 'ex1'
        ex2 = 'ex2'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(220, ex1)]
        msgs2 = [send(150, 1), throw(230, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex1)]

    def test_with_latest_from_throw_error(self):
        ex1 = 'ex1'
        ex2 = 'ex2'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(220, ex1)]
        msgs2 = [send(150, 1), throw(230, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex1)]

    def test_with_latest_from_never_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(220, ex)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_with_latest_from_throw_never(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(220, ex)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_with_latest_from_some_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_with_latest_from_throw_some(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_with_latest_from_no_throw_after_complete_left(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(220)]
        msgs2 = [send(150, 1), throw(230, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(220)]

    def test_with_latest_from_throw_after_complete_right(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(220)]
        msgs2 = [send(150, 1), throw(230, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(230, ex)]

    def test_with_latest_from_interleaved_with_tail(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), close(230)]
        msgs2 = [send(150, 1), send(220, 3), send(230, 5), send(235, 6), send(240, 7), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [send(225, 3 + 4), close(230)]

    def test_with_latest_from_consecutive(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), close(230)]
        msgs2 = [send(150, 1), send(235, 6), send(240, 7), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(230)]

    def test_with_latest_from_consecutive_end_with_error_left(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), throw(230, ex)]
        msgs2 = [send(150, 1), send(235, 6), send(240, 7), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(230, ex)]

    def test_with_latest_from_consecutive_end_with_error_right(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), close(230)]
        msgs2 = [send(150, 1), send(235, 6), send(240, 7), throw(245, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.with_latest_from(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [send(235, 4 + 6), send(240, 4 + 7), throw(245, ex)]

    def test_with_latest_from_mapper_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(225, 2), close(230)]
        msgs2 = [send(150, 1), send(220, 3), close(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: _raise(ex))

        results = scheduler.start(create)
        assert results.messages == [throw(225, ex)]

    def test_with_latest_from_repeat_last_left_value(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), send(230, 5), close(235)]
        msgs2 = [send(150, 1), send(220, 3), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.with_latest_from(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [send(225, 3 + 4), send(230, 3 + 5), close(235)]

if __name__ == '__main__':
    unittest.main()
