import unittest

from rx.core import Observable
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


class TestForEach(unittest.TestCase):

    def test_for_each_argument_checking(self):
        some = Observable.just(42).to_blocking()
        self.assertRaises(TypeError, lambda: Observable(None).to_blocking().for_each(lambda x: x))
        self.assertRaises(TypeError, lambda: some.for_each(lambda: None))

    def test_for_each_empty(self):
        lst = []
        Observable.empty().to_blocking().for_each(lambda x: lst.append(x))
        assert(lst == [])

    def test_For_each_index_empty(self):
        lstX = []
        Observable.empty().to_blocking().for_each(lambda x, i: lstX.append(x))
        assert(lstX == [])

    def test_for_each_return(self):
        lst = []
        Observable.return_value(42).to_blocking().for_each(lambda x: lst.append(x))
        assert(lst == [42])

    def test_for_each_index_return(self):
        lstX = []
        lstI = []

        def action(x, i):
            lstX.append(x)
            lstI.append(i)

        Observable.return_value(42).to_blocking().for_each(action)
        assert(lstX == [42])
        assert(lstI == [0])

    def test_for_each_throws(self):
        ex = "ex"
        xs = Observable.throw(ex)
        self.assertRaises(Exception, lambda: xs.to_blocking().for_each(lambda x: _raise(ex)))

    def test_for_each_index_throws(self):
        ex = Exception()
        xs = Observable.throw(ex)
        self.assertRaises(Exception, lambda:xs.to_blocking().for_each(lambda x, i: _raise(ex)))

    def test_for_each_some_data(self):
        lstX = []
        Observable.range(10, 10).to_blocking().for_each(lambda x: lstX.append(x))
        assert(lstX == [x for x in range(10, 20)])

    def test_for_each_index_some_data(self):
        lstX = []
        lstI = []

        def action(x, i):
            lstX.append(x)
            lstI.append(i)

        Observable.range(10, 10).to_blocking().for_each(action)
        assert(lstX == [x for x in range(10, 20)])
        assert(lstI == [x for x in range(10)])

    def test_for_each_on_next_throws(self):
        ex = Exception()
        xs = Observable.range(0, 10)
        self.assertRaises(RxException, lambda: xs.to_blocking().for_each(lambda x: _raise(ex)))

    def test_for_each_index_on_next_throws(self):
        ex = Exception()
        xs = Observable.range(0, 10)

        def action(x, i):
            _raise(ex)
        self.assertRaises(RxException, lambda: xs.to_blocking().for_each(action))
