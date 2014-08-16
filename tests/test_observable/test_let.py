import unittest

from rx import Observable
from rx.testing import ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestLet(unittest.TestCase):
    def test_let_calls_function_immediately(self):
        called = [False]

        def func(x):
            called[0] = True
            return x

        Observable.empty().let_bind(func)
        assert(called[0])
