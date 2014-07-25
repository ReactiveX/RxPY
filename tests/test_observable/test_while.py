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
	def test_while_always_false(self):
	    scheduler = TestScheduler()
	    xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
	    
	    def create():
	        def predicate(x):
	            return False

	        return Observable.while_do(predicate, xs)
	    results = scheduler.start(create)
	    
	    results.messages.assert_equal(on_completed(200))
	    xs.subscriptions.assert_equal()

# def test_While_AlwaysTrue():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
#     results = scheduler.start(function () {
#         return Observable.whileDo(function () {
#             return True
#         }, xs)
    
#     results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_next(750, 1), on_next(800, 2), on_next(850, 3), on_next(900, 4))
#     xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1000))


# def test_While_AlwaysTrue_Throw():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(onError(50, ex))
#     results = scheduler.start(function () {
#         return Observable.whileDo(function () {
#             return True
#         }, xs)
    
#     results.messages.assert_equal(onError(250, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_While_AlwaysTrue_Infinite():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1))
#     results = scheduler.start(function () {
#         return Observable.whileDo(function () {
#             return True
#         }, xs)
    
#     results.messages.assert_equal(on_next(250, 1))
#     xs.subscriptions.assert_equal(subscribe(200, 1000))


# def test_While_SometimesTrue():
#     var n, results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
#     n = 0
#     results = scheduler.start(function () {
#         return Observable.whileDo(function () {
#             return ++n < 3
#         }, xs)
    
#     results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_completed(700))
#     xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700))


# def test_While_SometimesThrows():
#     var ex, n, results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
#     n = 0
#     ex = 'ex'
#     results = scheduler.start(function () {
#         return Observable.whileDo(function () {
#             if (++n < 3) {
#                 return True
#             } else {
#                 throw ex
#             }
#         }, xs)
    
#     results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), onError(700, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700))
