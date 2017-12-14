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


class TestCatch(unittest.TestCase):

    def test_catch_no_errors(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(220, 3), close(230)]
        msgs2 = [send(240, 5), close(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.catch_exception(o2)
        results = scheduler.start(create)

        assert results.messages == [send(210, 2), send(220, 3), close(230)]

    def test_catch_never(self):
        scheduler = TestScheduler()
        msgs2 = [send(240, 5), close(250)]
        o1 = Observable.never()
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.catch_exception(o2)
        results = scheduler.start(create)

        assert results.messages == []

    def test_catch_empty(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(230)]
        msgs2 = [send(240, 5), close(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.catch_exception(o2)

        results = scheduler.start(create)
        assert results.messages == [close(230)]

    def test_catch_return(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(230)]
        msgs2 = [send(240, 5), close(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.catch_exception(o2)

        results = scheduler.start(create)
        assert results.messages == [send(210, 2), close(230)]

    def test_catch_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(220, 3), throw(230, ex)]
        msgs2 = [send(240, 5), close(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.catch_exception(o2)

        results = scheduler.start(create)
        assert results.messages == [send(210, 2), send(220, 3), send(240, 5), close(250)]

    def test_catch_error_never(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(220, 3), throw(230, ex)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = Observable.never()
        def create():
            return o1.catch_exception(o2)

        results = scheduler.start(create)
        assert results.messages == [send(210, 2), send(220, 3)]

    def test_catch_error_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(220, 3), throw(230, 'ex1')]
        msgs2 = [send(240, 4), throw(250, ex)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.catch_exception(o2)

        results = scheduler.start(create)
        assert results.messages == [send(210, 2), send(220, 3), send(240, 4), throw(250, ex)]

    def test_catch_multiple(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(215, ex)]
        msgs2 = [send(220, 3), throw(225, ex)]
        msgs3 = [send(230, 4), close(235)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)

        def create():
            return Observable.catch_exception(o1, o2, o3)

        results = scheduler.start(create)
        assert results.messages == [send(210, 2), send(220, 3), send(230, 4), close(235)]

    def test_catch_error_specific_caught(self):
        ex = 'ex'
        handler_called = [False]
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(220, 3), throw(230, ex)]
        msgs2 = [send(240, 4), close(250)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            def handler(e):
                handler_called[0] = True
                return o2

            return o1.catch_exception(handler)

        results = scheduler.start(create)

        assert results.messages == [send(210, 2), send(220, 3), send(240, 4), close(250)]
        assert(handler_called[0])

    def test_catch_error_specific_caught_immediate(self):
        ex = 'ex'
        handler_called = [False]
        scheduler = TestScheduler()
        msgs2 = [send(240, 4), close(250)]
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            def handler(e):
                handler_called[0] = True
                return o2

            return Observable.throw_exception('ex').catch_exception(handler)

        results = scheduler.start(create)

        assert results.messages == [send(240, 4), close(250)]
        assert(handler_called[0])

    def test_catch_handler_throws(self):
        ex = 'ex'
        ex2 = 'ex2'
        handler_called = [False]
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), send(220, 3), throw(230, ex)]
        o1 = scheduler.create_hot_observable(msgs1)

        def create():
            def handler(e):
                handler_called[0] = True
                raise Exception(ex2)
            return o1.catch_exception(handler)

        results = scheduler.start(create)

        assert results.messages == [send(210, 2), send(220, 3), throw(230, ex2)]
        assert(handler_called[0])

    def test_catch_nested_outer_catches(self):
        ex = 'ex'
        first_handler_called = [False]
        second_handler_called = [False]
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(215, ex)]
        msgs2 = [send(220, 3), close(225)]
        msgs3 = [send(220, 4), close(225)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)

        def create():
            def handler1(e):
                first_handler_called[0] = True
                return o2
            def handler2(e):
                second_handler_called[0] = True
                return o3
            return o1.catch_exception(handler1).catch_exception(handler2)

        results = scheduler.start(create)

        assert results.messages == [send(210, 2), send(220, 3), close(225)]
        assert(first_handler_called[0])
        assert(not second_handler_called[0])

    def test_catch_throw_from_nested_catch(self):
        ex = 'ex'
        ex2 = 'ex'
        first_handler_called = [False]
        second_handler_called = [False]
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), throw(215, ex)]
        msgs2 = [send(220, 3), throw(225, ex2)]
        msgs3 = [send(230, 4), close(235)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)

        def create():
            def handler1(e):
                first_handler_called[0] = True
                assert(e == ex)
                return o2
            def handler2(e):
                second_handler_called[0] = True
                assert(e == ex2)
                return o3
            return o1.catch_exception(handler1).catch_exception(handler2)

        results = scheduler.start(create)

        assert results.messages == [send(210, 2), send(220, 3), send(230, 4), close(235)]
        assert(first_handler_called[0])
        assert(second_handler_called[0])
