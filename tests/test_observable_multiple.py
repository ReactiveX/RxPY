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

class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


# def test_MergeConcat_Basic():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400))
#     results = scheduler.start(create)
#         return xs.merge(2)
#
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_next(670, 9), on_next(700, 10), on_completed(760))
#     xs.subscriptions.assert_equal(subscribe(200, 760))
#
# def test_MergeConcat_Basic_Long():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400))
#     results = scheduler.start(create)
#         return xs.merge(2)
#
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_next(690, 9), on_next(720, 10), on_completed(780))
#     xs.subscriptions.assert_equal(subscribe(200, 780))
#
# def test_MergeConcat_Basic_Wide():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(420, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(450))
#     results = scheduler.start(create)
#         return xs.merge(3)
#
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(280, 6), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 7), on_next(380, 8), on_next(630, 9), on_next(660, 10), on_completed(720))
#     xs.subscriptions.assert_equal(subscribe(200, 720))
#
# def test_MergeConcat_Basic_Late():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(420, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(750))
#     results = scheduler.start(create)
#         return xs.merge(3)
#
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(280, 6), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 7), on_next(380, 8), on_next(630, 9), on_next(660, 10), on_completed(750))
#     xs.subscriptions.assert_equal(subscribe(200, 750))
#
# def test_MergeConcat_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400))
#     results = scheduler.startWithDispose(function () {
#         return xs.merge(2)
#     }, 450)
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7))
#     xs.subscriptions.assert_equal(subscribe(200, 450))
#
# def test_MergeConcat_OuterError():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_error(400, ex))
#     results = scheduler.start(create)
#         return xs.merge(2)
#
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_error(400, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 400))
#
# def test_MergeConcat_InnerError():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_error(140, ex))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400))
#     results = scheduler.start(create)
#         return xs.merge(2)
#
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_error(490, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 490))
#

# test("Rx.Observable.catchException() does not lose subscription to underlying observable", 12, function () {
#     var subscribes = 0,
#             unsubscribes = 0,
#             tracer = Rx.Observable.create(function (observer) { ++subscribes return function () { ++unsubscribes } ,
#             s

#     // Try it without catchException()
#     s = tracer.subscribe()
#     strictEqual(subscribes, 1, "1 subscribes")
#     strictEqual(unsubscribes, 0, "0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "After dispose: 1 unsubscribes")

#     // Now try again with catchException(Observable):
#     subscribes = unsubscribes = 0
#     s = tracer.catchException(Rx.Observable.never()).subscribe()
#     strictEqual(subscribes, 1, "catchException(Observable): 1 subscribes")
#     strictEqual(unsubscribes, 0, "catchException(Observable): 0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "catchException(Observable): After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "catchException(Observable): After dispose: 1 unsubscribes")

#     // And now try again with catchException(function()):
#     subscribes = unsubscribes = 0
#     s = tracer.catchException(function () { return Rx.Observable.never() .subscribe()
#     strictEqual(subscribes, 1, "catchException(function): 1 subscribes")
#     strictEqual(unsubscribes, 0, "catchException(function): 0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "catchException(function): After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "catchException(function): After dispose: 1 unsubscribes") // this one FAILS (unsubscribes is 0)
#

if __name__ == '__main__':
    test_combine_latest_return_empty()