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

class TestAsObservable(unittest.TestCase):
    def test_as_observable_hides(self):
        some_observable = Observable.empty()
        assert(some_observable.as_observable() != some_observable)

# def test_as_observable_Never():
#     var results, scheduler
#     scheduler = TestScheduler()
#     results = scheduler.start(create)
#         return Rx.Observable.never().as_observable()

#     results.messages.assert_equal()

# def test_as_observable_Empty():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     results = scheduler.start(create)
#         return xs.as_observable()
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'C' and results[0].time == 250)

# def test_as_observable_Throw():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
#     results = scheduler.start(create)
#         return xs.as_observable()
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'E' and results[0].value.exception == ex and results[0].time == 250)

# def test_as_observable_Return():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.as_observable()
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].value.value == 2 and results[0].time == 220)
#     assert(results[1].value.kind == 'C' and results[1].time == 250)

# def test_as_observable_IsNotEager():
#     var scheduler, subscribed, xs
#     scheduler = TestScheduler()
#     subscribed = false
#     xs = Rx.Observable.create(function (obs) {
#         var disp
#         subscribed = true
#         disp = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250)).subscribe(obs)
#         return function () {
#             return disp.dispose()
#         }

#     xs.as_observable()
#     assert(!subscribed)
#     scheduler.start(create)
#         return xs.as_observable()

#     assert(subscribed)


