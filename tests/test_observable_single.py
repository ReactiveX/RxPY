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

# def test_Materialize_Never():
#     var results, scheduler
#     scheduler = TestScheduler()
#     results = scheduler.start(create)
#         return Rx.Observable.never().materialize()
    
#     results.messages.assert_equal()

# def test_Materialize_Empty():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     results = scheduler.start(create)
#         return xs.materialize()
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'C' and results[0].time == 250)
#     assert(results[1].value.kind == 'C' and results[1].time == 250)

# def test_Materialize_Return():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.materialize()
#     }).messages
#     equal(3, results.length)
#     assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'N' and results[0].value.value.value == 2 and results[0].time == 210)
#     assert(results[1].value.kind == 'N' and results[1].value.value.kind == 'C' and results[1].time == 250)
#     assert(results[2].value.kind == 'C' and results[1].time == 250)

# def test_Materialize_Throw():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
#     results = scheduler.start(create)
#         return xs.materialize()
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].value.value.kind == 'E' and results[0].value.value.exception == ex)
#     assert(results[1].value.kind == 'C')

# def test_Materialize_Dematerialize_Never():
#     var results, scheduler
#     scheduler = TestScheduler()
#     results = scheduler.start(create)
#         return Rx.Observable.never().materialize().dematerialize()
    
#     results.messages.assert_equal()

# def test_Materialize_Dematerialize_Empty():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     results = scheduler.start(create)
#         return xs.materialize().dematerialize()
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'C' and results[0].time == 250)

# def test_Materialize_Dematerialize_Return():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.materialize().dematerialize()
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].value.value == 2 and results[0].time == 210)
#     assert(results[1].value.kind == 'C')

# def test_Materialize_Dematerialize_Throw():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
#     results = scheduler.start(create)
#         return xs.materialize().dematerialize()
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'E' and results[0].value.exception == ex and results[0].time == 250)

# def test_StartWith():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.startWith(1)
#     }).messages
#     equal(3, results.length)
#     assert(results[0].value.kind == 'N' and results[0].value.value == 1 and results[0].time == 200)
#     assert(results[1].value.kind == 'N' and results[1].value.value == 2 and results[1].time == 220)
#     assert(results[2].value.kind == 'C')


def sequenceEqual(arr1, arr2):
    if  len(arr1) != len(arr2):
        return False

    for i in range(len(arr1)):
         if arr1[i] != arr2[i]:
             return false
    return True

# def test_buffer_count_partial_window():
#      scheduler = TestScheduler()
#      xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
     
#      def create():
#         return xs.buffer_with_count(5)
#      results = scheduler.start(create).messages
#      equal(2, results.length)
#      assert(sequenceEqual(results[0].value.value, [2, 3, 4, 5]) and results[0].time == 250)
#      assert(results[1].value.kind == 'C' and results[1].time == 250)

# def test_Buffer_Count_FullWindows():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     results = scheduler.start(create)
#         return xs.bufferWithCount(2)
#     }).messages
#     equal(3, results.length)
#     assert(sequenceEqual(results[0].value.value, [2, 3]) and results[0].time == 220)
#     assert(sequenceEqual(results[1].value.value, [4, 5]) and results[1].time == 240)
#     assert(results[2].value.kind == 'C' and results[2].time == 250)

# def test_Buffer_Count_FullAndPartialWindows():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     results = scheduler.start(create)
#         return xs.bufferWithCount(3)
#     }).messages
#     equal(3, results.length)
#     assert(sequenceEqual(results[0].value.value, [2, 3, 4]) and results[0].time == 230)
#     assert(sequenceEqual(results[1].value.value, [5]) and results[1].time == 250)
#     assert(results[2].value.kind == 'C' and results[2].time == 250)

# def test_Buffer_Count_Error():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_error(250, 'ex'))
#     results = scheduler.start(create)
#         return xs.bufferWithCount(5)
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'E' and results[0].time == 250)

# def test_Buffer_Count_Skip_Less():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     results = scheduler.start(create)
#         return xs.bufferWithCount(3, 1)
#     }).messages
#     equal(5, results.length)
#     assert(sequenceEqual(results[0].value.value, [2, 3, 4]) and results[0].time == 230)
#     assert(sequenceEqual(results[1].value.value, [3, 4, 5]) and results[1].time == 240)
#     assert(sequenceEqual(results[2].value.value, [4, 5]) and results[2].time == 250)
#     assert(sequenceEqual(results[3].value.value, [5]) and results[3].time == 250)
#     assert(results[4].value.kind == 'C' and results[4].time == 250)

# def test_Buffer_Count_Skip_More():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     results = scheduler.start(create)
#         return xs.bufferWithCount(2, 3)
#     }).messages
#     equal(3, results.length)
#     assert(sequenceEqual(results[0].value.value, [2, 3]) and results[0].time == 220)
#     assert(sequenceEqual(results[1].value.value, [5]) and results[1].time == 250)
#     assert(results[2].value.kind == 'C' and results[2].time == 250)

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

# def test_DistinctUntilChanged_Never():
#     var results, scheduler
#     scheduler = TestScheduler()
#     results = scheduler.start(create)
#         return Rx.Observable.never().distinctUntilChanged()
    
#     results.messages.assert_equal()

# def test_DistinctUntilChanged_Empty():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged()
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'C' and results[0].time == 250)

# def test_DistinctUntilChanged_Return():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(220, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged()
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].time == 220 and results[0].value.value == 2)
#     assert(results[1].value.kind == 'C' and results[1].time == 250)

# def test_DistinctUntilChanged_Throw():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged()
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'E' and results[0].time == 250 and results[0].value.exception == ex)

# def test_DistinctUntilChanged_AllChanges():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged()
#     }).messages
#     equal(5, results.length)
#     assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
#     assert(results[1].value.kind == 'N' and results[1].time == 220 and results[1].value.value == 3)
#     assert(results[2].value.kind == 'N' and results[2].time == 230 and results[2].value.value == 4)
#     assert(results[3].value.kind == 'N' and results[3].time == 240 and results[3].value.value == 5)
#     assert(results[4].value.kind == 'C' and results[4].time == 250)

# def test_DistinctUntilChanged_AllSame():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 2), on_next(230, 2), on_next(240, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged()
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
#     assert(results[1].value.kind == 'C' and results[1].time == 250)

# def test_DistinctUntilChanged_SomeChanges():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(215, 3), on_next(220, 3), on_next(225, 2), on_next(230, 2), on_next(230, 1), on_next(240, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged()
#     }).messages
#     equal(6, results.length)
#     assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
#     assert(results[1].value.kind == 'N' and results[1].time == 215 and results[1].value.value == 3)
#     assert(results[2].value.kind == 'N' and results[2].time == 225 and results[2].value.value == 2)
#     assert(results[3].value.kind == 'N' and results[3].time == 230 and results[3].value.value == 1)
#     assert(results[4].value.kind == 'N' and results[4].time == 240 and results[4].value.value == 2)
#     assert(results[5].value.kind == 'C' and results[5].time == 250)

# def test_DistinctUntilChanged_Comparer_AllEqual():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged(void 0, function (x, y) {
#             return true
        
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
#     assert(results[1].value.kind == 'C' and results[1].time == 250)

# def test_DistinctUntilChanged_Comparer_AllDifferent():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 2), on_next(230, 2), on_next(240, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged(void 0, function (x, y) {
#             return false
        
#     }).messages
#     equal(5, results.length)
#     assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
#     assert(results[1].value.kind == 'N' and results[1].time == 220 and results[1].value.value == 2)
#     assert(results[2].value.kind == 'N' and results[2].time == 230 and results[2].value.value == 2)
#     assert(results[3].value.kind == 'N' and results[3].time == 240 and results[3].value.value == 2)
#     assert(results[4].value.kind == 'C' and results[4].time == 250)

# def test_DistinctUntilChanged_KeySelector_Div2():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 4), on_next(230, 3), on_next(240, 5), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged(function (x) {
#             return x % 2
        
#     }).messages
#     equal(3, results.length)
#     assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
#     assert(results[1].value.kind == 'N' and results[1].time == 230 and results[1].value.value == 3)
#     assert(results[2].value.kind == 'C' and results[2].time == 250)

# def test_DistinctUntilChanged_KeySelectorThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged(function (x) {
#             throw ex
        
    
#     results.messages.assert_equal(on_error(210, ex))

# def test_DistinctUntilChanged_ComparerThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
#     results = scheduler.start(create)
#         return xs.distinctUntilChanged(void 0, function (x, y) {
#             throw ex
        
    
#     results.messages.assert_equal(on_next(210, 2), on_error(220, ex))

# def test_Finally_OnlyCalledOnce_Empty():
#     var d, invasserteCount, someObservable
#     invasserteCount = 0
#     someObservable = Rx.Observable.empty().finallyAction(function () {
#         return invasserteCount++
    
#     d = someObservable.subscribe()
#     d.dispose()
#     d.dispose()
#     equal(1, invasserteCount)

# def test_Finally_Empty():
#     var invasserted, results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     invasserted = false
#     results = scheduler.start(create)
#         return xs.finallyAction(function () {
#             return invasserted = true
        
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'C' and results[0].time == 250)
#     assert(invasserted)

# def test_Finally_Return():
#     var invasserted, results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     invasserted = false
#     results = scheduler.start(create)
#         return xs.finallyAction(function () {
#             return invasserted = true
        
#     }).messages
#     equal(2, results.length)
#     assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
#     assert(results[1].value.kind == 'C' and results[1].time == 250)
#     assert(invasserted)

# def test_Finally_Throw():
#     var ex, invasserted, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(250, ex))
#     invasserted = false
#     results = scheduler.start(create)
#         return xs.finallyAction(function () {
#             return invasserted = true
        
#     }).messages
#     equal(1, results.length)
#     assert(results[0].value.kind == 'E' and results[0].time == 250 and results[0].value.exception == ex)
#     assert(invasserted)

# def test_Do_ShouldSeeAllValues():
#     var i, scheduler, sum, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = 0
#     sum = 2 + 3 + 4 + 5
#     scheduler.start(create)
#         return xs.doAction(function (x) {
#             i++
#             return sum -= x
        
    
#     equal(4, i)
#     equal(0, sum)

# def test_Do_PlainAction():
#     var i, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = 0
#     scheduler.start(create)
#         return xs.doAction(function (x) {
#             return i++
        
    
#     equal(4, i)

# def test_Do_NextCompleted():
#     var completed, i, scheduler, sum, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = 0
#     sum = 2 + 3 + 4 + 5
#     completed = false
#     scheduler.start(create)
#         return xs.doAction(function (x) {
#             i++
#             sum -= x
#         }, undefined, function () {
#             completed = true
        
    
#     equal(4, i)
#     equal(0, sum)
#     assert(completed)

# def test_Do_NextCompleted_Never():
#     var completed, i, scheduler
#     scheduler = TestScheduler()
#     i = 0
#     completed = false
#     scheduler.start(create)
#         return Rx.Observable.never().doAction(function (x) {
#             i++
#         }, undefined, function () {
#             completed = true
        
    
#     equal(0, i)
#     assert(!completed)

# def test_Do_NextError():
#     var ex, i, sawError, scheduler, sum, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_error(250, ex))
#     i = 0
#     sum = 2 + 3 + 4 + 5
#     sawError = false
#     scheduler.start(create)
#         return xs.doAction(function (x) {
#             i++
#             sum -= x
#         }, function (e) {
#             sawError = e == ex
        
    
#     equal(4, i)
#     equal(0, sum)
#     assert(sawError)

# def test_Do_NextErrorNot():
#     var i, sawError, scheduler, sum, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = 0
#     sum = 2 + 3 + 4 + 5
#     sawError = false
#     scheduler.start(create)
#         return xs.doAction(function (x) {
#             i++
#             sum -= x
#         }, function (e) {
#             sawError = true
        
    
#     equal(4, i)
#     equal(0, sum)
#     assert(!sawError)

# def test_Do_NextErrorCompleted():
#     var hasCompleted, i, sawError, scheduler, sum, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = 0
#     sum = 2 + 3 + 4 + 5
#     sawError = false
#     hasCompleted = false
#     scheduler.start(create)
#         return xs.doAction(function (x) {
#             i++
#             sum -= x
#         }, function (e) {
#             sawError = true
#         }, function () {
#             hasCompleted = true
        
    
#     equal(4, i)
#     equal(0, sum)
#     assert(!sawError)
#     assert(hasCompleted)

# def test_Do_NextErrorCompletedError():
#     var ex, hasCompleted, i, sawError, scheduler, sum, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_error(250, ex))
#     i = 0
#     sum = 2 + 3 + 4 + 5
#     sawError = false
#     hasCompleted = false
#     scheduler.start(create)
#         return xs.doAction(function (x) {
#             i++
#             sum -= x
#         }, function (e) {
#             sawError = ex == e
#         }, function () {
#             hasCompleted = true
        
    
#     equal(4, i)
#     equal(0, sum)
#     assert(sawError)
#     assert(!hasCompleted)

# def test_Do_NextErrorCompletedNever():
#     var hasCompleted, i, sawError, scheduler
#     scheduler = TestScheduler()
#     i = 0
#     sawError = false
#     hasCompleted = false
#     scheduler.start(create)
#         return Rx.Observable.never().doAction(function (x) {
#             i++
#         }, function (e) {
#             sawError = true
#         }, function () {
#             hasCompleted = true
        
    
#     equal(0, i)
#     assert(!sawError)
#     assert(!hasCompleted)

# def test_Do_Observer_SomeDataWithError():
#     var ex, hasCompleted, i, sawError, scheduler, sum, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_error(250, ex))
#     i = 0
#     sum = 2 + 3 + 4 + 5
#     sawError = false
#     hasCompleted = false
#     scheduler.start(create)
#         return xs.doAction(Rx.Observer.create(function (x) {
#             i++
#             sum -= x
#         }, function (e) {
#             sawError = e == ex
#         }, function () {
#             hasCompleted = true
#         }))
    
#     equal(4, i)
#     equal(0, sum)
#     assert(sawError)
#     assert(!hasCompleted)

# def test_Do_Observer_SomeDataWithError():
#     var hasCompleted, i, sawError, scheduler, sum, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     i = 0
#     sum = 2 + 3 + 4 + 5
#     sawError = false
#     hasCompleted = false
#     scheduler.start(create)
#         return xs.doAction(Rx.Observer.create(function (x) {
#             i++
#             sum -= x
#         }, function (e) {
#             sawError = true
#         }, function () {
#             hasCompleted = true
#         }))
    
#     equal(4, i)
#     equal(0, sum)
#     assert(!sawError)
#     assert(hasCompleted)

# def test_Do1422_Next_NextThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.doAction(function () {
#             throw ex
        
    
#     results.messages.assert_equal(on_error(210, ex))

# def test_Do1422_NextCompleted_NextThrows():
#     var ex, results, scheduler, xs, _undefined
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.doAction(function () {
#             throw ex
#         }, _undefined, function () { 
    
#     results.messages.assert_equal(on_error(210, ex))

# def test_Do1422_NextCompleted_CompletedThrows():
#     var ex, results, scheduler, xs, _undefined
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.doAction(function () { }, _undefined, function () {
#             throw ex
        
    
#     results.messages.assert_equal(on_next(210, 2), on_error(250, ex))

# def test_Do1422_NextError_NextThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.doAction(function () {
#             throw ex
#         }, function () { 
    
#     results.messages.assert_equal(on_error(210, ex))

# def test_Do1422_NextError_NextThrows():
#     var ex1, ex2, results, scheduler, xs
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex1))
#     results = scheduler.start(create)
#         return xs.doAction(function () { }, function () {
#             throw ex2
        
    
#     results.messages.assert_equal(on_error(210, ex2))

# def test_Do1422_NextErrorCompleted_NextThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.doAction(function () {
#             throw ex
#         }, function () { }, function () { 
    
#     results.messages.assert_equal(on_error(210, ex))

# def test_Do1422_NextErrorCompleted_ErrorThrows():
#     var ex1, ex2, results, scheduler, xs
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex1))
#     results = scheduler.start(create)
#         return xs.doAction(function () { }, function () {
#             throw ex2
#         }, function () { 
    
#     results.messages.assert_equal(on_error(210, ex2))

# def test_Do1422_NextErrorCompleted_CompletedThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.doAction(function () { }, function () { }, function () {
#             throw ex
        
    
#     results.messages.assert_equal(on_next(210, 2), on_error(250, ex))

# def test_Do1422_Observer_NextThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.doAction(Rx.Observer.create(function () {
#             throw ex
#         }, function () { }, function () { }))
    
#     results.messages.assert_equal(on_error(210, ex))

# def test_Do1422_Observer_ErrorThrows():
#     var ex1, ex2, results, scheduler, xs
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex1))
#     results = scheduler.start(create)
#         return xs.doAction(Rx.Observer.create(function () { }, function () {
#             throw ex2
#         }, function () { }))
    
#     results.messages.assert_equal(on_error(210, ex2))

# def test_Do1422_Observer_CompletedThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     results = scheduler.start(create)
#         return xs.doAction(Rx.Observer.create(function () { }, function () { }, function () {
#             throw ex
#         }))
    
#     results.messages.assert_equal(on_next(210, 2), on_error(250, ex))

# def test_TakeLast_Zero_Completed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     results = scheduler.start(create)
#         return xs.takeLast(0)
    
#     results.messages.assert_equal(on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLast_Zero_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     results = scheduler.start(create)
#         return xs.takeLast(0)
    
#     results.messages.assert_equal(on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLast_Zero_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     results = scheduler.start(create)
#         return xs.takeLast(0)
    
#     results.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_TakeLast_One_Completed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     results = scheduler.start(create)
#         return xs.takeLast(1)
    
#     results.messages.assert_equal(on_next(650, 9), on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLast_One_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     results = scheduler.start(create)
#         return xs.takeLast(1)
    
#     results.messages.assert_equal(on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLast_One_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     results = scheduler.start(create)
#         return xs.takeLast(1)
    
#     results.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_TakeLast_Three_Completed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     results = scheduler.start(create)
#         return xs.takeLast(3)
    
#     results.messages.assert_equal(on_next(650, 7), on_next(650, 8), on_next(650, 9), on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLast_Three_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     results = scheduler.start(create)
#         return xs.takeLast(3)
    
#     results.messages.assert_equal(on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLast_Three_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     results = scheduler.start(create)
#         return xs.takeLast(3)
    
#     results.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_SkipLast_Zero_Completed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     results = scheduler.start(create)
#         return xs.skipLast(0)
    
#     results.messages.assert_equal(on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_SkipLast_Zero_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     results = scheduler.start(create)
#         return xs.skipLast(0)
    
#     results.messages.assert_equal(on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_SkipLast_Zero_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     results = scheduler.start(create)
#         return xs.skipLast(0)
    
#     results.messages.assert_equal(on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_SkipLast_One_Completed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     results = scheduler.start(create)
#         return xs.skipLast(1)
    
#     results.messages.assert_equal(on_next(250, 2), on_next(270, 3), on_next(310, 4), on_next(360, 5), on_next(380, 6), on_next(410, 7), on_next(590, 8), on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_SkipLast_One_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     results = scheduler.start(create)
#         return xs.skipLast(1)
    
#     results.messages.assert_equal(on_next(250, 2), on_next(270, 3), on_next(310, 4), on_next(360, 5), on_next(380, 6), on_next(410, 7), on_next(590, 8), on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_SkipLast_One_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     results = scheduler.start(create)
#         return xs.skipLast(1)
    
#     results.messages.assert_equal(on_next(250, 2), on_next(270, 3), on_next(310, 4), on_next(360, 5), on_next(380, 6), on_next(410, 7), on_next(590, 8))
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_SkipLast_Three_Completed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     results = scheduler.start(create)
#         return xs.skipLast(3)
    
#     results.messages.assert_equal(on_next(310, 2), on_next(360, 3), on_next(380, 4), on_next(410, 5), on_next(590, 6), on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_SkipLast_Three_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     results = scheduler.start(create)
#         return xs.skipLast(3)
    
#     results.messages.assert_equal(on_next(310, 2), on_next(360, 3), on_next(380, 4), on_next(410, 5), on_next(590, 6), on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_SkipLast_Three_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     results = scheduler.start(create)
#         return xs.skipLast(3)
    
#     results.messages.assert_equal(on_next(310, 2), on_next(360, 3), on_next(380, 4), on_next(410, 5), on_next(590, 6))
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

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


# // TakeLastBuffer

# function arrayEqual(arr1, arr2) {
#     if (arr1.length !== arr2.length) return false
#     for (var i = 0, len = arr1.length i < len i++) {
#         if (arr1[i] !== arr2[i]) return false
#     }
#     return true
# }

# def test_TakeLastBuffer_Zero_Completed():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(0)
    
#     res.messages.assert_equal(on_next(650, function (lst) {
#         return lst.length == 0
#     }), on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLastBuffer_Zero_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(0)
    
#     res.messages.assert_equal(on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLastBuffer_Zero_Disposed():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(0)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_TakeLastBuffer_One_Completed():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(1)
    
#     res.messages.assert_equal(on_next(650, function (lst) {
#         return arrayEqual(lst, [9])
#     }), on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLastBuffer_One_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(1)
    
#     res.messages.assert_equal(on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLastBuffer_One_Disposed():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(1)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_TakeLastBuffer_Three_Completed():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_completed(650))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(3)
    
#     res.messages.assert_equal(on_next(650, function (lst) {
#         return arrayEqual(lst, [7, 8, 9])
#     }), on_completed(650))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLastBuffer_Three_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9), on_error(650, ex))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(3)
    
#     res.messages.assert_equal(on_error(650, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 650))

# def test_TakeLastBuffer_Three_Disposed():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(250, 3), on_next(270, 4), on_next(310, 5), on_next(360, 6), on_next(380, 7), on_next(410, 8), on_next(590, 9))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer(3)
    
#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

