import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestIsEmpty(unittest.TestCase):
	def test_min_int32_empty(self):
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
	    
	    def create():
	   		return xs.min()
	    res = scheduler.start(create=create).messages
	    assert(1 == len(res))
	    assert(res[0].value.kind == 'E' and res[0].value.exception)
	    assert(res[0].time == 250)

	def test_in_int32_return(self):
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
	    res = scheduler.start(create=lambda: xs.min()).messages
	    res.assert_equal(on_next(250, 2), on_completed(250))

	def test_min_int32_some(self):
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))
	    res = scheduler.start(create=lambda: xs.min()).messages
	    res.assert_equal(on_next(250, 2), on_completed(250))

	def test_min_int32_throw(self):
	    ex = 'ex'
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
	    res = scheduler.start(create=lambda: xs.min()).messages
	    res.assert_equal(on_error(210, ex))

	def test_min_int32_never(self):
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(150, 1))
	    res = scheduler.start(create=lambda: xs.min()).messages
	    res.assert_equal()

