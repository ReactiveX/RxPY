import unittest
import pytest

from rx.core import AnonymousObservable, Observable
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

        with pytest.raises(TypeError):
            AnonymousObservable(None).to_blocking().for_each(lambda x: x)

        with pytest.raises(TypeError):
            some.for_each(lambda: None)

    def test_for_each_empty(self):
        lst = []
        rx.empty().to_blocking().for_each(lambda x: lst.append(x))
        assert(lst == [])

    def test_For_each_index_empty(self):
        lst_x = []
        rx.empty().to_blocking().for_each(lambda x: lst_x.append(x))
        assert(lst_x == [])

    def test_for_each_return(self):
        lst = []
        rx.return_value(42).to_blocking().for_each(lambda x: lst.append(x))
        assert(lst == [42])

    def test_for_each_index_return(self):
        lst_x = []
        lst_i = []

        def action(x, i):
            lst_x.append(x)
            lst_i.append(i)

        rx.return_value(42).to_blocking().for_each(action_indexed=action)
        assert(lst_x == [42])
        assert(lst_i == [0])

    def test_for_each_throws(self):
        ex = "ex"
        xs = rx.throw(ex)
        self.assertRaises(Exception, lambda: xs.to_blocking().for_each(lambda x: _raise(ex)))

    def test_for_each_index_throws(self):
        ex = Exception()
        xs = rx.throw(ex)
        self.assertRaises(Exception, lambda:xs.to_blocking().for_each(lambda x: _raise(ex)))

    def test_for_each_some_data(self):
        lst_x = []
        Observable.range(10, 20).to_blocking().for_each(lambda x: lst_x.append(x))
        assert(lst_x == [x for x in range(10, 20)])

    def test_for_each_index_some_data(self):
        lst_x = []
        lst_i = []

        def action(x, i):
            lst_x.append(x)
            lst_i.append(i)

        Observable.range(10, 20).to_blocking().for_each(action_indexed=action)
        assert(lst_x == [x for x in range(10, 20)])
        assert(lst_i == [x for x in range(10)])

    def test_for_each_on_next_throws(self):
        ex = Exception()
        xs = Observable.range(0, 10)
        self.assertRaises(RxException, lambda: xs.to_blocking().for_each(lambda x: _raise(ex)))

    def test_for_each_index_on_next_throws(self):
        ex = Exception()
        xs = Observable.range(0, 10)

        def action(x):
            _raise(ex)
        self.assertRaises(RxException, lambda: xs.to_blocking().for_each(action))
