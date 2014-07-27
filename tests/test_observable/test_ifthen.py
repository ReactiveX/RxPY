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

class TestIfThen(unittest.TestCase):
	def test_if_true(self):
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(210, 1), on_next(250, 2), on_completed(300))
	    ys = scheduler.create_hot_observable(on_next(310, 3), on_next(350, 4), on_completed(400))
	    
	    def create():
	    	return Observable.if_then(lambda: True, xs, ys)
	    results = scheduler.start(create=create)
	        
	    results.messages.assert_equal(on_next(210, 1), on_next(250, 2), on_completed(300))
	    xs.subscriptions.assert_equal(subscribe(200, 300))
	    ys.subscriptions.assert_equal()

	def test_if_false(self):
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(210, 1), on_next(250, 2), on_completed(300))
	    ys = scheduler.create_hot_observable(on_next(310, 3), on_next(350, 4), on_completed(400))
	    def create():
	    	return Observable.if_then(lambda: False, xs, ys)
	    results = scheduler.start(create=create)
	    
	    results.messages.assert_equal(on_next(310, 3), on_next(350, 4), on_completed(400))
	    xs.subscriptions.assert_equal()
	    ys.subscriptions.assert_equal(subscribe(200, 400))

	def test_if_throw(self):
	    ex = 'ex'
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(210, 1), on_next(250, 2), on_completed(300))
	    ys = scheduler.create_hot_observable(on_next(310, 3), on_next(350, 4), on_completed(400))
	    
	    def create():
	    	def condition():
	    		raise Exception(ex)
	    	return Observable.if_then(condition, xs, ys)
	    results = scheduler.start(create=create)
	    
	    results.messages.assert_equal(on_error(200, ex))
	    xs.subscriptions.assert_equal()
	    ys.subscriptions.assert_equal()

	def test_if_dispose(self):
	    scheduler = TestScheduler()
	    xs = scheduler.create_hot_observable(on_next(210, 1), on_next(250, 2))
	    ys = scheduler.create_hot_observable(on_next(310, 3), on_next(350, 4), on_completed(400))
	    
	    def create():
	    	return Observable.if_then(lambda: True, xs, ys)
	    results = scheduler.start(create=create)
	    
	    results.messages.assert_equal(on_next(210, 1), on_next(250, 2))
	    xs.subscriptions.assert_equal(subscribe(200, 1000))
	    ys.subscriptions.assert_equal()
