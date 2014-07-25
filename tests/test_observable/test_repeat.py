import unittest

from rx.observable import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import Disposable, SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestRepeat(unittest.TestCase):
    def test_repeat_value_count_zero(self):
        scheduler = TestScheduler()

        def create():
            return Observable.repeat(42, 0, scheduler)
        results = scheduler.start(create)
        
        results.messages.assert_equal(on_completed(200))

    def test_repeat_value_count_one(self):
        scheduler = TestScheduler()

        def create():
            return Observable.repeat(42, 1, scheduler)
        
        results = scheduler.start(create)
        results.messages.assert_equal(on_next(201, 42), on_completed(201))

    def test_repeat_value_count_ten(self):
        scheduler = TestScheduler()
        
        def create():    
            return Observable.repeat(42, 10, scheduler)
        
        results = scheduler.start(create)
        results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42), on_next(207, 42), on_next(208, 42), on_next(209, 42), on_next(210, 42), on_completed(210))

    def test_repeat_value_count_dispose(self):
        scheduler = TestScheduler()

        def create():
            return Observable.repeat(42, 10, scheduler)

        results = scheduler.start(create, disposed=207)
        results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42))

    def test_repeat_value(self):
        scheduler = TestScheduler()
        def create():
            return Observable.repeat(42, -1, scheduler)

        results = scheduler.start(create, disposed=207)
        results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42))
