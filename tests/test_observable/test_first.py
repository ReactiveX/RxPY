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

class TestFirst(unittest.TestCase):
    def test_first_async_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
        def create():
            return xs.first()

        res = scheduler.start(create=create)

        def _on_error(e):
            return e != None

        res.messages.assert_equal(on_error(250, _on_error))

        xs.subscriptions.assert_equal(subscribe(200, 250))

# def test_FirstAsync_One():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first()

#     res.messages.assert_equal(on_next(210, 2), on_completed(210))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstAsync_Many():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first()

#     res.messages.assert_equal(on_next(210, 2), on_completed(210))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstAsync_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.first()

#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstAsync_Predicate():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first(function (x) {
#             return x % 2 == 1


#     res.messages.assert_equal(on_next(220, 3), on_completed(220))
#     xs.subscriptions.assert_equal(subscribe(200, 220))


# def test_FirstAsync_Predicate_None():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first(function (x) {
#             return x > 10


#     res.messages.assert_equal(on_error(250, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_FirstAsync_Predicate_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_error(220, ex))
#     res = scheduler.start(create=create)
#         return xs.first(function (x) {
#             return x % 2 == 1


#     res.messages.assert_equal(on_error(220, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 220))


# def test_FirstAsync_PredicateThrows():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first(function (x) {
#             if (x < 4) {
#                 return False
#             } else {
#                 throw ex
#             }


#     res.messages.assert_equal(on_error(230, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

