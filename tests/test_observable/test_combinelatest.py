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


class TestCombineLatest(unittest.TestCase):

    def test_combine_latest_never_never(self):
        scheduler = TestScheduler()
        e1 = Observable.never()
        e2 = Observable.never()

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_combine_latest_never_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(210)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_combine_latest_empty_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(210)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_combine_latest_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), close(210)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(210)]

    def test_combine_latest_empty_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(215)]

    def test_combine_latest_return_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(210)]
        msgs2 = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [close(215)]

    def test_combine_latest_never_feturn(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(215, 2), close(220)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = Observable.never()

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_combine_latest_return_never(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), send(215, 2), close(210)]
        e1 = scheduler.create_hot_observable(msgs)
        e2 = Observable.never()

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == []

    def test_combine_latest_return_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), send(220, 3), close(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [send(220, 2 + 3), close(240)]

    def test_combine_latest_empty_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_combine_latest_error_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_combine_latest_return_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_combine_latest_throw_return(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_combine_latest_throw_throw(self):
        ex1 = 'ex1'
        ex2 = 'ex2'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), throw(220, ex1)]
        msgs2 = [send(150, 1), throw(230, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex1)]

    def test_combine_latest_error_throw(self):
        ex1 = 'ex1'
        ex2 = 'ex2'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(220, ex1)]
        msgs2 = [send(150, 1), throw(230, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex1)]

    def test_combine_latest_throw_error(self):
        ex1 = 'ex1'
        ex2 = 'ex2'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(220, ex1)]
        msgs2 = [send(150, 1), throw(230, ex2)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex1)]

    def test_combine_latest_never_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(220, ex)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_combine_latest_throw_never(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [send(150, 1), throw(220, ex)]
        e1 = Observable.never()
        e2 = scheduler.create_hot_observable(msgs)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_combine_latest_some_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_combine_latest_throw_some(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), throw(220, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

    def test_combine_latest_throw_after_complete_left(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(220)]
        msgs2 = [send(150, 1), throw(230, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(230, ex)]

    def test_combine_latest_throw_after_complete_right(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(220)]
        msgs2 = [send(150, 1), throw(230, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(230, ex)]

    def test_combine_latest_interleaved_with_tail(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), close(230)]
        msgs2 = [send(150, 1), send(220, 3), send(230, 5), send(235, 6), send(240, 7), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [send(220, 2 + 3), send(225, 3 + 4), send(230, 4 + 5), send(235, 4 + 6), send(240, 4 + 7), close(250)]

    def test_combine_latest_consecutive(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), close(230)]
        msgs2 = [send(150, 1), send(235, 6), send(240, 7), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [send(235, 4 + 6), send(240, 4 + 7), close(250)]

    def test_combine_latest_consecutive_end_with_error_left(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), throw(230, ex)]
        msgs2 = [send(150, 1), send(235, 6), send(240, 7), close(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [throw(230, ex)]

    def test_combine_latest_consecutive_end_with_error_right(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), send(225, 4), close(230)]
        msgs2 = [send(150, 1), send(235, 6), send(240, 7), throw(245, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e2.combine_latest(e1, lambda x, y: x + y)

        results = scheduler.start(create)
        assert results.messages == [send(235, 4 + 6), send(240, 4 + 7), throw(245, ex)]

    def test_combine_latest_mapper_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(215, 2), close(230)]
        msgs2 = [send(150, 1), send(220, 3), close(240)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.combine_latest(e2, lambda x, y: _raise(ex))

        results = scheduler.start(create)
        assert results.messages == [throw(220, ex)]

if __name__ == '__main__':
    unittest.main()
