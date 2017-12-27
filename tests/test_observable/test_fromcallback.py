import unittest

from rx import Observable
from rx.testing import ReactiveTest

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


class TestFromCallback(unittest.TestCase):
    def test_from_callback(self):
        res = Observable.from_callback(lambda cb: cb(True))()

        def send(r):
            self.assertEqual(r, True)

        def throw(err):
            assert(False)

        def close():
            assert(True)

        res.subscribe_callbacks(send, throw, close)

    def test_from_callback_single(self):
        res = Observable.from_callback(lambda file, cb: cb(file))('file.txt')

        def send(r):
            self.assertEqual(r, 'file.txt')

        def throw(err):
            print(err)
            assert(False)

        def close():
            assert(True)

        res.subscribe_callbacks(send, throw, close)

    def test_from_node_callback_mapper(self):
        res = Observable.from_callback(
            lambda f,s,t,cb: cb(f,s,t),
            lambda r: r[0]
        )(1,2,3)

        def send(r):
            self.assertEqual(r, 1)

        def throw(err):
            assert(False)

        def close():
            assert(True)

        res.subscribe_callbacks(send, throw, close)

