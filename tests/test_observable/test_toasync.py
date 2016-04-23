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


class TestToAsync(unittest.TestCase):
    def test_to_async_context(self):
        class Context:
            def __init__(self):
                self.value = 42
            def func(self, x):
                return self.value + x

        scheduler = TestScheduler()

        def create():
            context = Context()
            return Observable.to_async(context.func, scheduler)(42)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(200, 84),
            on_completed(200)
        )

    def test_to_async0(self):
        scheduler = TestScheduler()

        def create():
            def func():
                return 0

            return Observable.to_async(func, scheduler)()

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(200, 0),
            on_completed(200)
        )

    def test_to_async1(self):
        scheduler = TestScheduler()

        def create():
            def func(x):
                return x

            return Observable.to_async(func, scheduler)(1)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(200, 1),
            on_completed(200)
         )

    def test_to_async2(self):
        scheduler = TestScheduler()

        def create():
            def func(x, y):
                return x + y

            return Observable.to_async(func, scheduler)(1, 2)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(200, 3),
            on_completed(200)
        )

    def test_to_async3(self):
        scheduler = TestScheduler()

        def create():
            def func(x, y, z):
                return x + y + z

            return Observable.to_async(func, scheduler)(1, 2, 3)

        res = scheduler.start(create)


        res.messages.assert_equal(
            on_next(200, 6),
            on_completed(200)
        )

    def test_to_async4(self):
        scheduler = TestScheduler()

        def create():
            def func(a, b, c, d):
                return a + b + c + d

            return Observable.to_async(func, scheduler)(1, 2, 3, 4)
        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(200, 10),
            on_completed(200)
        )

    def test_to_async_error0(self):
        ex = Exception()

        scheduler = TestScheduler()

        def create():
            def func():
                raise ex
            return Observable.to_async(func, scheduler)()

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_error(200, ex)
        )

    def test_to_async_error1(self):
        ex = Exception()

        scheduler = TestScheduler()

        def create():
            def func(a):
                raise ex
            return Observable.to_async(func, scheduler)(1)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_error(200, ex)
        )

    def test_to_async_error2(self):
        ex = Exception()

        scheduler = TestScheduler()

        def create():
            def func(a, b):
                raise ex
            return Observable.to_async(func, scheduler)(1, 2)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_error(200, ex)
        )

    def test_to_async_error0(self):
        ex = Exception()

        scheduler = TestScheduler()

        def create():
            def func(a, b, c):
                raise ex
            return Observable.to_async(func, scheduler)(1, 2, 3)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_error(200, ex)
        )

    def test_to_async_error0(self):
        ex = Exception()

        scheduler = TestScheduler()

        def create():
            def func(a, b, c, d):
                raise ex
            return Observable.to_async(func, scheduler)(1, 2, 3, 4)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_error(200, ex)
        )
