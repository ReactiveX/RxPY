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

class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)

class TestExpand(unittest.TestCase):

    def test_expand_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_completed(300))
        
        def create():
            def selector():
                return scheduler.create_cold_observable(on_next(100, 1), on_next(200, 2), on_completed(300))
            
            return xs.expand(selector, scheduler)
        results = scheduler.start(create)
    
        results.messages.assert_equal(on_completed(300))
        xs.subscriptions.assert_equal(subscribe(201, 300))

# def test_expand_Error(self):
#     var ex, results, scheduler, xs
#     scheduler = TestScheduler()
#     ex = 'ex'
#     xs = scheduler.create_hot_observable(on_error(300, ex))
#     results = scheduler.start(create)
#         return xs.expand(function (x) {
#             return scheduler.create_cold_observable(on_next(100 + x, 2 * x), on_next(200 + x, 3 * x), on_completed(300 + x))
#         }, scheduler)
#     
#     results.messages.assert_equal(on_error(300, ex))
#     xs.subscriptions.assert_equal(subscribe(201, 300))
# 

# def test_expand_Never(self):
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     results = scheduler.start(create)
#         return xs.expand(function (x) {
#             return scheduler.create_cold_observable(on_next(100 + x, 2 * x), on_next(200 + x, 3 * x), on_completed(300 + x))
#         }, scheduler)
#     
#     results.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(201, 1000))
# 

# def test_expand_Basic(self):
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(550, 1), on_next(850, 2), on_completed(950))
#     results = scheduler.start(create)
#         return xs.expand(function (x) {
#             return scheduler.create_cold_observable(on_next(100, 2 * x), on_next(200, 3 * x), on_completed(300))
#         }, scheduler)
#     
#     results.messages.assert_equal(on_next(550, 1), on_next(651, 2), on_next(751, 3), on_next(752, 4), on_next(850, 2), on_next(852, 6), on_next(852, 6), on_next(853, 8), on_next(951, 4), on_next(952, 9), on_next(952, 12), on_next(953, 12), on_next(953, 12), on_next(954, 16))
#     xs.subscriptions.assert_equal(subscribe(201, 950))
# 

# def test_expand_Throw(self):
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(550, 1), on_next(850, 2), on_completed(950))
#     results = scheduler.start(create)
#         return xs.expand(function (x) {
#             throw ex
#         }, scheduler)
#     
#     results.messages.assert_equal(on_next(550, 1), on_error(550, ex))
#     xs.subscriptions.assert_equal(subscribe(201, 550))
# 