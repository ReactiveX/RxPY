from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created




# def test_If_Default_Completed():
#     var b, results, scheduler, xs
#     b = False
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(110, 1), on_next(220, 2), on_next(330, 3), on_completed(440))
#     scheduler.scheduleAbsolute(150, function () {
#         b = True
    
#     results = scheduler.start(function () {
#         return Observable.ifThen(function () {
#             return b
#         }, xs)
    
#     results.messages.assert_equal(on_next(220, 2), on_next(330, 3), on_completed(440))
#     xs.subscriptions.assert_equal(subscribe(200, 440))


# def test_If_Default_Error():
#     var b, ex, results, scheduler, xs
#     ex = 'ex'
#     b = False
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(110, 1), on_next(220, 2), on_next(330, 3), onError(440, ex))
#     scheduler.scheduleAbsolute(150, function () {
#         b = True
    
#     results = scheduler.start(function () {
#         return Observable.ifThen(function () {
#             return b
#         }, xs)
    
#     results.messages.assert_equal(on_next(220, 2), on_next(330, 3), onError(440, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 440))


# def test_If_Default_Never():
#     var b, results, scheduler, xs
#     b = False
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(110, 1), on_next(220, 2), on_next(330, 3))
#     scheduler.scheduleAbsolute(150, function () {
#         b = True
    
#     results = scheduler.start(function () {
#         return Observable.ifThen(function () {
#             return b
#         }, xs)
    
#     results.messages.assert_equal(on_next(220, 2), on_next(330, 3))
#     xs.subscriptions.assert_equal(subscribe(200, 1000))


# def test_If_Default_Other():
#     var b, results, scheduler, xs
#     b = True
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(110, 1), on_next(220, 2), on_next(330, 3), onError(440, 'ex'))
#     scheduler.scheduleAbsolute(150, function () {
#         b = False
    
#     results = scheduler.start(function () {
#         return Observable.ifThen(function () {
#             return b
#         }, xs)
    
#     results.messages.assert_equal(on_completed(200))
#     xs.subscriptions.assert_equal()


# // must call `QUnit.start()` if using QUnit < 1.3.0 with Node.js or any
# // version of QUnit with Narwhal, Rhino, or RingoJS
# if (!window.document) {
#     QUnit.start()
# }
# }(typeof global == 'object' && global || this))