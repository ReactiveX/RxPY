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


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestFromCallback(unittest.TestCase):
    def test_from_callback(self):
        res = Observable.from_callback(lambda cb: cb(True))()

        def on_next(r):
            self.assertEqual(r, True)

        def on_error(err):
            assert(False)

        def on_completed():
            assert(True)

        res.subscribe(on_next, on_error, on_completed)

    def test_from_callback_single(self):
        res = Observable.from_callback(lambda file, cb: cb(file))('file.txt')

        def on_next(r):
            self.assertEqual(r, 'file.txt')

        def on_error(err):
            print(err)
            assert(False)

        def on_completed():
            assert(True)

        res.subscribe(on_next, on_error, on_completed)

    def test_from_node_callback_selector(self):
        res = Observable.from_callback(
            lambda f,s,t,cb: cb(f,s,t),
            lambda r: r[0]
        )(1,2,3)

        def on_next(r):
            self.assertEqual(r, 1)

        def on_error(err):
            assert(False)

        def on_completed():
            assert(True)

        res.subscribe(on_next, on_error, on_completed)

