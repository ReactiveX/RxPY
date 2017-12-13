import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestOnErrorResumeNext(unittest.TestCase):
    def test_throw_resume_next_no_errors(self):
        scheduler = TestScheduler()
        msgs1 = [
            send(150, 1),
            send(210, 2),
            send(220, 3),
            close(230)]

        msgs2 = [
            send(240, 4),
            close(250)]

        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.throw_resume_next(o2)

        results = scheduler.start(create)
        assert results.messages == [
            send(210, 2),
            send(220, 3),
            send(240, 4),
            close(250)]

    def test_throw_resume_next_error(self):
        scheduler = TestScheduler()
        msgs1 = [
            send(150, 1),
            send(210, 2),
            send(220, 3),
            throw(230, 'ex')]

        msgs2 = [
            send(240, 4),
            close(250)]

        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.throw_resume_next(o2)
        results = scheduler.start(create)

        assert results.messages == [
            send(210, 2),
            send(220, 3),
            send(240, 4),
            close(250)]

    def test_throw_resume_next_error_multiple(self):
        scheduler = TestScheduler()
        msgs1 = [
            send(150, 1),
            send(210, 2),
            throw(220, 'ex')]

        msgs2 = [
            send(230, 4),
            throw(240, 'ex')]

        msgs3 = [close(250)]

        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)
        def create():
            return Observable.throw_resume_next(o1, o2, o3)
        results = scheduler.start(create)

        assert results.messages == [
            send(210, 2), send(230, 4), close(250)]

    def test_throw_resume_next_empty_return_throw_and_more(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), close(205)]
        msgs2 = [send(215, 2), close(220)]
        msgs3 = [send(225, 3), send(230, 4), close(235)]
        msgs4 = [throw(240, 'ex')]
        msgs5 = [send(245, 5), close(250)]

        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)
        o4 = scheduler.create_hot_observable(msgs4)
        o5 = scheduler.create_hot_observable(msgs5)

        def create():
            return Observable.throw_resume_next(o1, o2, o3, o4, o5)
        results = scheduler.start(create)

        assert results.messages == [
            send(215, 2),
            send(225, 3),
            send(230, 4),
            send(245, 5),
            close(250)]

    def test_throw_resume_next_empty_return_throw_and_more_ii(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [
            send(150, 1), send(210, 2), close(220)]
        msgs2 = [throw(230, ex)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        def create():
            return o1.throw_resume_next(o2)
        results = scheduler.start(create)

        assert results.messages == [send(210, 2), close(230)]

    def test_throw_resume_next_single_source_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [throw(230, ex)]
        o1 = scheduler.create_hot_observable(msgs1)
        def create():
            return Observable.throw_resume_next(o1)
        results = scheduler.start(create)

        assert results.messages == [close(230)]

    def test_throw_resume_next_end_with_never(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(220)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = Observable.never()

        def create():
            return Observable.throw_resume_next(o1, o2)
        results = scheduler.start(create)

        assert results.messages == [send(210, 2)]

    def test_throw_resume_next_start_with_never(self):
        scheduler = TestScheduler()
        msgs1 = [send(150, 1), send(210, 2), close(220)]
        o1 = Observable.never()
        o2 = scheduler.create_hot_observable(msgs1)

        def create():
            return Observable.throw_resume_next(o1, o2)

        results = scheduler.start(create)

        assert results.messages == []

    def test_throw_resume_next_start_with_factory(self):
        scheduler = TestScheduler()
        msgs1 = [
            send(150, 1),
            send(210, 2),
            send(220, 3),
            throw(230, 'ex')]
        o1 = scheduler.create_hot_observable(msgs1)

        def factory(ex):
            assert(ex == "ex")
            msgs2 = [send(240, 4), close(250)]
            o2 = scheduler.create_hot_observable(msgs2)
            return o2

        def create():
            return Observable.throw_resume_next(o1, factory)

        results = scheduler.start(create)

        assert results.messages == [
            send(210, 2),
            send(220, 3),
            send(240, 4),
            close(250)]


