import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestOnErrorResumeNext(unittest.TestCase):
    def test_on_error_resume_next_no_errors(self):
        scheduler = TestScheduler()
        msgs1 = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_completed(230)]

        msgs2 = [
            on_next(240, 4),
            on_completed(250)]

        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.on_error_resume_next(o2)

        results = scheduler.start(create)
        results.messages.assert_equal(
            on_next(210, 2),
            on_next(220, 3),
            on_next(240, 4),
            on_completed(250))

    def test_on_error_resume_next_error(self):
        scheduler = TestScheduler()
        msgs1 = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_error(230, 'ex')]

        msgs2 = [
            on_next(240, 4),
            on_completed(250)]

        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)

        def create():
            return o1.on_error_resume_next(o2)
        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(220, 3),
            on_next(240, 4),
            on_completed(250))

    def test_on_error_resume_next_error_multiple(self):
        scheduler = TestScheduler()
        msgs1 = [
            on_next(150, 1),
            on_next(210, 2),
            on_error(220, 'ex')]

        msgs2 = [
            on_next(230, 4),
            on_error(240, 'ex')]

        msgs3 = [on_completed(250)]

        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)
        def create():
            return Observable.on_error_resume_next(o1, o2, o3)
        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(210, 2), on_next(230, 4), on_completed(250))

    def test_on_error_resume_next_empty_return_throw_and_more(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(205)]
        msgs2 = [on_next(215, 2), on_completed(220)]
        msgs3 = [on_next(225, 3), on_next(230, 4), on_completed(235)]
        msgs4 = [on_error(240, 'ex')]
        msgs5 = [on_next(245, 5), on_completed(250)]

        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        o3 = scheduler.create_hot_observable(msgs3)
        o4 = scheduler.create_hot_observable(msgs4)
        o5 = scheduler.create_hot_observable(msgs5)

        def create():
            return Observable.on_error_resume_next(o1, o2, o3, o4, o5)
        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(215, 2),
            on_next(225, 3),
            on_next(230, 4),
            on_next(245, 5),
            on_completed(250))

    def test_on_error_resume_next_empty_return_throw_and_more_ii(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [
            on_next(150, 1), on_next(210, 2), on_completed(220)]
        msgs2 = [on_error(230, ex)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = scheduler.create_hot_observable(msgs2)
        def create():
            return o1.on_error_resume_next(o2)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 2), on_completed(230))

    def test_on_error_resume_next_single_source_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_error(230, ex)]
        o1 = scheduler.create_hot_observable(msgs1)
        def create():
            return Observable.on_error_resume_next(o1)
        results = scheduler.start(create)

        results.messages.assert_equal(on_completed(230))

    def test_on_error_resume_next_end_with_never(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(220)]
        o1 = scheduler.create_hot_observable(msgs1)
        o2 = Observable.never()

        def create():
            return Observable.on_error_resume_next(o1, o2)
        results = scheduler.start(create)

        results.messages.assert_equal(on_next(210, 2))

    def test_on_error_resume_next_start_with_never(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(220)]
        o1 = Observable.never()
        o2 = scheduler.create_hot_observable(msgs1)

        def create():
            return Observable.on_error_resume_next(o1, o2)

        results = scheduler.start(create)

        results.messages.assert_equal()

    def test_on_error_resume_next_start_with_factory(self):
        scheduler = TestScheduler()
        msgs1 = [
            on_next(150, 1),
            on_next(210, 2),
            on_next(220, 3),
            on_error(230, 'ex')]
        o1 = scheduler.create_hot_observable(msgs1)

        def factory(ex):
            assert(ex == "ex")
            msgs2 = [on_next(240, 4), on_completed(250)]
            o2 = scheduler.create_hot_observable(msgs2)
            return o2

        def create():
            return Observable.on_error_resume_next(o1, factory)

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(210, 2),
            on_next(220, 3),
            on_next(240, 4),
            on_completed(250))


