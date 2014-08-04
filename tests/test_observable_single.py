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

def sequenceEqual(arr1, arr2):
    if  len(arr1) != len(arr2):
        return False

    for i in range(len(arr1)):
         if arr1[i] != arr2[i]:
             return false
    return True


# def test_AsObservable_Hides():
#     var someObservable
#     someObservable = Rx.Observable.empty()
#     assert(someObservable.asObservable() !== someObservable)

# def test_AsObservable_Never():
#     var results, scheduler
#     scheduler = TestScheduler()
#     results = scheduler.start(create)
#         return Rx.Observable.never().asObservable()
    
#     results.messages.assert_equal()

# def test_AsObservable_Empty():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     results = scheduler.start(create)
#         return xs.asObservable()
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'C' and results[0].time == 250)

# def test_AsObservable_Throw():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
#     results = scheduler.start(create)
#         return xs.asObservable()
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'E' and results[0].value.exception == ex and results[0].time == 250)

# def test_AsObservable_Return():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.asObservable()
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].value.value == 2 and results[0].time == 220)
#     assert(results[1].value.kind == 'C' and results[1].time == 250)

# def test_AsObservable_IsNotEager():
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
    
#     xs.asObservable()
#     assert(!subscribed)
#     scheduler.start(create)
#         return xs.asObservable()
    
#     assert(subscribed)




# def test_IgnoreValues_Basic():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     results = scheduler.start(create)
#         return xs.ignoreElements()
    
#     results.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_IgnoreValues_Completed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(610))
#     results = scheduler.start(create)
#         return xs.ignoreElements()
    
#     results.messages.assert_equal(on_completed(610))
#     xs.subscriptions.assert_equal(subscribe(200, 610))

# def test_IgnoreValues_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(610, ex))
#     results = scheduler.start(create)
#         return xs.ignoreElements()
    
#     results.messages.assert_equal(on_error(610, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 610))

def test_window_with_count_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    def create():
        def proj(w, i):
            print("proj")
            return w.select(lambda x: str(i) + ' ' + str(x))
        return xs.window_with_count(3, 2).select(proj).merge_observable()
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"), on_next(380, "2 7"), on_next(420, "2 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_window_with_count_disposed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
    
    def create():
        def proj(w, i):
            return w.select(lambda x: str(i) + ' ' + str(x))        
        return xs.window_with_count(3, 2).select(proj).merge_observable()
    
    results = scheduler.start(create, disposed=370)
    results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"))
    xs.subscriptions.assert_equal(subscribe(200, 370))

# def test_WindowWithCount_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))
#     results = scheduler.start(create)
#         return xs.windowWithCount(3, 2).select(function (w, i) {
#             return w.select(function (x) {
#                 return i.toString() + ' ' + x.toString()
            
#         }).mergeObservable()
    
#     results.messages.assert_equal(on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "0 4"), on_next(280, "1 4"), on_next(320, "1 5"), on_next(350, "1 6"), on_next(350, "2 6"), on_next(380, "2 7"), on_next(420, "2 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_error(600, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 600))

# def test_BufferWithCount_Basic():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
#     results = scheduler.start(create)
#         return xs.bufferWithCount(3, 2).select(function (x) {
#             return x.toString()
        
    
#     results.messages.assert_equal(on_next(280, "2,3,4"), on_next(350, "4,5,6"), on_next(420, "6,7,8"), on_next(600, "8,9"), on_completed(600))
#     xs.subscriptions.assert_equal(subscribe(200, 600))

# def test_BufferWithCount_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(100, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(380, 7), on_next(420, 8), on_next(470, 9), on_completed(600))
#     results = scheduler.startWithDispose(function () {
#         return xs.bufferWithCount(3, 2).select(function (x) {
#             return x.toString()
        
#     }, 370)
#     results.messages.assert_equal(on_next(280, "2,3,4"), on_next(350, "4,5,6"))
#     xs.subscriptions.assert_equal(subscribe(200, 370))

# def test_DefaultIfEmpty_NonEmpty1():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_completed(420))
#     results = scheduler.start(create)
#         return xs.defaultIfEmpty()
    
#     results.messages.assert_equal(on_next(280, 42), on_next(360, 43), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))

# def test_DefaultIfEmpty_NonEmpty2():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_completed(420))
#     results = scheduler.start(create)
#         return xs.defaultIfEmpty(-1)
    
#     results.messages.assert_equal(on_next(280, 42), on_next(360, 43), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))

# def test_DefaultIfEmpty_Empty1():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_completed(420))
#     results = scheduler.start(create)
#         return xs.defaultIfEmpty(null)
    
#     results.messages.assert_equal(on_next(420, null), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))

# def test_DefaultIfEmpty_Empty2():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_completed(420))
#     results = scheduler.start(create)
#         return xs.defaultIfEmpty(-1)
    
#     results.messages.assert_equal(on_next(420, -1), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))

# def test_Distinct_DefaultComparer_AllDistinct():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 4), on_next(300, 2), on_next(350, 1), on_next(380, 3), on_next(400, 5), on_completed(420))
#     results = scheduler.start(create)
#         return xs.distinct()
    
#     results.messages.assert_equal(on_next(280, 4), on_next(300, 2), on_next(350, 1), on_next(380, 3), on_next(400, 5), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))

# def test_Distinct_DefaultComparer_SomeDuplicates():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 4), on_next(300, 2), on_next(350, 2), on_next(380, 3), on_next(400, 4), on_completed(420))
#     results = scheduler.start(create)
#         return xs.distinct()
    
#     results.messages.assert_equal(on_next(280, 4), on_next(300, 2), on_next(380, 3), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))

# def test_Distinct_KeySelectory_AllDistinct():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 8), on_next(300, 4), on_next(350, 2), on_next(380, 6), on_next(400, 10), on_completed(420))
#     results = scheduler.start(create)
#         return xs.distinct(function (x) {
#             return x / 2
        
    
#     results.messages.assert_equal(on_next(280, 8), on_next(300, 4), on_next(350, 2), on_next(380, 6), on_next(400, 10), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))

# def test_Distinct_KeySelector_SomeDuplicates():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 4), on_next(300, 2), on_next(350, 3), on_next(380, 7), on_next(400, 5), on_completed(420))
#     results = scheduler.start(create)
#         return xs.distinct(function (x) {
#             return Math.floor(x / 2)
        
    
#     results.messages.assert_equal(on_next(280, 4), on_next(300, 2), on_next(380, 7), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))

# def test_Distinct_KeySelector_Throws():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 3), on_next(300, 2), on_next(350, 1), on_next(380, 0), on_next(400, 4), on_completed(420))
#     results = scheduler.start(create)
#         return xs.distinct(function (x) {
#             if (x == 0) {
#                 throw ex
#             } else {
#                 return Math.floor(x / 2)
#             }
        
    
#     results.messages.assert_equal(on_next(280, 3), on_next(350, 1), on_error(380, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 380))


