from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

# def test_while_always_false():
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
    
#     def factory():
#         def predicate(x):
#             return False

#         return Observable.while_do(predicate, xs)
#     results = scheduler.start_with_create(factory)
    
#     results.messages.assert_equal(on_completed(200))
#     xs.subscriptions.assert_equal()

# def test_While_AlwaysTrue():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
#     results = scheduler.start_with_create(function () {
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
#     results = scheduler.start_with_create(function () {
#         return Observable.whileDo(function () {
#             return True
#         }, xs)
    
#     results.messages.assert_equal(onError(250, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_While_AlwaysTrue_Infinite():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1))
#     results = scheduler.start_with_create(function () {
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
#     results = scheduler.start_with_create(function () {
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
#     results = scheduler.start_with_create(function () {
#         return Observable.whileDo(function () {
#             if (++n < 3) {
#                 return True
#             } else {
#                 throw ex
#             }
#         }, xs)
    
#     results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), onError(700, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700))


# def test_If_True():
#     var results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(250, 2), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(310, 3), on_next(350, 4), on_completed(400))
#     results = scheduler.start_with_create(function () {
#         return Observable.ifThen(function () {
#             return True
#         }, xs, ys)
    
#     results.messages.assert_equal(on_next(210, 1), on_next(250, 2), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))
#     ys.subscriptions.assert_equal()


# def test_If_False():
#     var results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(250, 2), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(310, 3), on_next(350, 4), on_completed(400))
#     results = scheduler.start_with_create(function () {
#         return Observable.ifThen(function () {
#             return False
#         }, xs, ys)
    
#     results.messages.assert_equal(on_next(310, 3), on_next(350, 4), on_completed(400))
#     xs.subscriptions.assert_equal()
#     ys.subscriptions.assert_equal(subscribe(200, 400))


# def test_If_Throw():
#     var ex, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(250, 2), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(310, 3), on_next(350, 4), on_completed(400))
#     results = scheduler.start_with_create(function () {
#         return Observable.ifThen(function () {
#             throw ex
#         }, xs, ys)
    
#     results.messages.assert_equal(onError(200, ex))
#     xs.subscriptions.assert_equal()
#     ys.subscriptions.assert_equal()


# def test_If_Dispose():
#     var results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(250, 2))
#     ys = scheduler.createHotObservable(on_next(310, 3), on_next(350, 4), on_completed(400))
#     results = scheduler.start_with_create(function () {
#         return Observable.ifThen(function () {
#             return True
#         }, xs, ys)
    
#     results.messages.assert_equal(on_next(210, 1), on_next(250, 2))
#     xs.subscriptions.assert_equal(subscribe(200, 1000))
#     ys.subscriptions.assert_equal()


# def test_DoWhile_AlwaysFalse():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
#     results = scheduler.start_with_create(function () {
#         return xs.doWhile(function () {
#             return False
        
    
#     results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_completed(450))
#     xs.subscriptions.assert_equal(subscribe(200, 450))


# def test_DoWhile_AlwaysTrue():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
#     results = scheduler.start_with_create(function () {
#         return xs.doWhile(function () {
#             return True
        
    
#     results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_next(750, 1), on_next(800, 2), on_next(850, 3), on_next(900, 4))
#     xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1000))


# def test_DoWhile_AlwaysTrue_Throw():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(onError(50, ex))
#     results = scheduler.start_with_create(function () {
#         return xs.doWhile(function () {
#             return True
        
    
#     results.messages.assert_equal(onError(250, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_DoWhile_AlwaysTrue_Infinite():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1))
#     results = scheduler.start_with_create(function () {
#         return xs.doWhile(function () {
#             return True
        
    
#     results.messages.assert_equal(on_next(250, 1))
#     xs.subscriptions.assert_equal(subscribe(200, 1000))


# def test_DoWhile_SometimesTrue():
#     var n, results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
#     n = 0
#     results = scheduler.start_with_create(function () {
#         return xs.doWhile(function () {
#             return ++n < 3
        
    
#     results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_next(750, 1), on_next(800, 2), on_next(850, 3), on_next(900, 4), on_completed(950))
#     xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950))


# def test_DoWhile_SometimesThrows():
#     var ex, n, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(150, 3), on_next(200, 4), on_completed(250))
#     n = 0
#     results = scheduler.start_with_create(function () {
#         return xs.doWhile(function () {
#             if (++n < 3) {
#                 return True
#             } else {
#                 throw ex
#             }
        
    
#     results.messages.assert_equal(on_next(250, 1), on_next(300, 2), on_next(350, 3), on_next(400, 4), on_next(500, 1), on_next(550, 2), on_next(600, 3), on_next(650, 4), on_next(750, 1), on_next(800, 2), on_next(850, 3), on_next(900, 4), onError(950, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950))


# def test_Case_One():
#     var map, results, scheduler, xs, ys, zs
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     zs = scheduler.createHotObservable(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
#     map = {
#         1: xs,
#         2: ys
#     }
#     results = scheduler.start_with_create(function () {
#         return Observable.switchCase(function () {
#             return 1
#         }, map, zs)
    
#     results.messages.assert_equal(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))
#     ys.subscriptions.assert_equal()
#     zs.subscriptions.assert_equal()


# def test_Case_Two():
#     var map, results, scheduler, xs, ys, zs
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     zs = scheduler.createHotObservable(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
#     map = {
#         1: xs,
#         2: ys
#     }
#     results = scheduler.start_with_create(function () {
#         return Observable.switchCase(function () {
#             return 2
#         }, map, zs)
    
#     results.messages.assert_equal(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     xs.subscriptions.assert_equal()
#     ys.subscriptions.assert_equal(subscribe(200, 310))
#     zs.subscriptions.assert_equal()


# def test_Case_Three():
#     var map, results, scheduler, xs, ys, zs
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     zs = scheduler.createHotObservable(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
#     map = {
#         1: xs,
#         2: ys
#     }
#     results = scheduler.start_with_create(function () {
#         return Observable.switchCase(function () {
#             return 3
#         }, map, zs)
    
#     results.messages.assert_equal(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
#     xs.subscriptions.assert_equal()
#     ys.subscriptions.assert_equal()
#     zs.subscriptions.assert_equal(subscribe(200, 320))


# def test_Case_Throw():
#     var ex, map, results, scheduler, xs, ys, zs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     zs = scheduler.createHotObservable(on_next(230, 21), on_next(240, 22), on_next(290, 23), on_completed(320))
#     map = {
#         1: xs,
#         2: ys
#     }
#     results = scheduler.start_with_create(function () {
#         return Observable.switchCase(function () {
#             throw ex
#         }, map, zs)
    
#     results.messages.assert_equal(onError(200, ex))
#     xs.subscriptions.assert_equal()
#     ys.subscriptions.assert_equal()
#     zs.subscriptions.assert_equal()


# def test_CaseWithDefault_One():
#     var map, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     map = {
#         1: xs,
#         2: ys
#     }
#     results = scheduler.start_with_create(function () {
#         return Observable.switchCase(function () {
#             return 1
#         }, map, scheduler)
    
#     results.messages.assert_equal(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))
#     ys.subscriptions.assert_equal()


# def test_CaseWithDefault_Two():
#     var map, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     map = {
#         1: xs,
#         2: ys
#     }
#     results = scheduler.start_with_create(function () {
#         return Observable.switchCase(function () {
#             return 2
#         }, map, scheduler)
    
#     results.messages.assert_equal(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     xs.subscriptions.assert_equal()
#     ys.subscriptions.assert_equal(subscribe(200, 310))


# def test_CaseWithDefault_Three():
#     var map, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     map = {
#         1: xs,
#         2: ys
#     }
#     results = scheduler.start_with_create(function () {
#         return Observable.switchCase(function () {
#             return 3
#         }, map, scheduler)
    
#     results.messages.assert_equal(on_completed(201))
#     xs.subscriptions.assert_equal()
#     ys.subscriptions.assert_equal()


# def test_CaseWithDefault_Throw():
#     var ex, map, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(210, 1), on_next(240, 2), on_next(270, 3), on_completed(300))
#     ys = scheduler.createHotObservable(on_next(220, 11), on_next(250, 12), on_next(280, 13), on_completed(310))
#     map = {
#         1: xs,
#         2: ys
#     }
#     results = scheduler.start_with_create(function () {
#         return Observable.switchCase(function () {
#             throw ex
#         }, map, scheduler)
    
#     results.messages.assert_equal(onError(200, ex))
#     xs.subscriptions.assert_equal()
#     ys.subscriptions.assert_equal()


# def test_For_Basic():
#     var results, scheduler
#     scheduler = TestScheduler()
#     results = scheduler.start_with_create(function () {
#         return Observable.forIn([1, 2, 3], function (x) {
#             return scheduler.create_cold_observable(on_next(x * 100 + 10, x * 10 + 1), on_next(x * 100 + 20, x * 10 + 2), on_next(x * 100 + 30, x * 10 + 3), on_completed(x * 100 + 40))
        
    
#     results.messages.assert_equal(on_next(310, 11), on_next(320, 12), on_next(330, 13), on_next(550, 21), on_next(560, 22), on_next(570, 23), on_next(890, 31), on_next(900, 32), on_next(910, 33), on_completed(920))


# def test_For_Throws():
#     var ex, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     results = scheduler.start_with_create(function () {
#         return Observable.forIn([1, 2, 3], function () {
#             throw ex
        
    
#     results.messages.assert_equal(onError(200, ex))


# def test_If_Default_Completed():
#     var b, results, scheduler, xs
#     b = False
#     scheduler = TestScheduler()
#     xs = scheduler.createHotObservable(on_next(110, 1), on_next(220, 2), on_next(330, 3), on_completed(440))
#     scheduler.scheduleAbsolute(150, function () {
#         b = True
    
#     results = scheduler.start_with_create(function () {
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
    
#     results = scheduler.start_with_create(function () {
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
    
#     results = scheduler.start_with_create(function () {
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
    
#     results = scheduler.start_with_create(function () {
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