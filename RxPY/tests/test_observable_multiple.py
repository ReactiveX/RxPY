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

def test_take_until_preempt_somedata_next():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_next(225, 99), on_completed(230)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_completed(225))

def test_take_until_preempt_somedata_error():
    ex = 'ex'
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_error(225, ex)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_error(225, ex))

def test_take_until_nopreempt_somedata_empty():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_completed(225)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)    
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))


def test_take_until_nopreempt_somedata_never():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    l = scheduler.create_hot_observable(l_msgs)
    r = Observable.never()
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)    
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

def test_take_until_preempt_never_next():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_next(225, 2), on_completed(250)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)

    def create():
        return l.take_until(r)

    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(225))

def test_take_until_preempt_never_error():
    ex = 'ex'
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_error(225, ex)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(225, ex))

def test_take_until_nopreempt_never_empty():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_completed(225)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_take_until_nopreempt_never_never():
    scheduler = TestScheduler()
    l = Observable.never()
    r = Observable.never()
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

# def test_Take_until_Preempt_BeforeFirstProduced():
#     var l, l_msgs, r, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
#     r_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
#     l = scheduler.create_hot_observable(l_msgs)
#     r = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return l.take_until(r)
#     
#     results.messages.assert_equal(on_completed(210))
# 

# def test_Take_until_Preempt_BeforeFirstProduced_RemainSilentAndProperDisposed():
#     var l, l_msgs, r, r_msgs, results, scheduler, sourceNotDisposed
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_error(215, 'ex'), on_completed(240)]
#     r_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
#     sourceNotDisposed = false
#     l = scheduler.create_hot_observable(l_msgs).doAction(function () {
#         sourceNotDisposed = true
#     
#     r = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return l.take_until(r)
#     
#     results.messages.assert_equal(on_completed(210))
#     ok(!sourceNotDisposed)
# 

# def test_Take_until_NoPreempt_AfterLastProduced_ProperDisposedSignal():
#     var l, l_msgs, r, r_msgs, results, scheduler, signalNotDisposed
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
#     r_msgs = [on_next(150, 1), on_next(250, 2), on_completed(260)]
#     signalNotDisposed = false
#     l = scheduler.create_hot_observable(l_msgs)
#     r = scheduler.create_hot_observable(r_msgs).doAction(function () {
#         signalNotDisposed = true
#     
#     results = scheduler.start(create)
#         return l.take_until(r)
#     
#     results.messages.assert_equal(on_next(230, 2), on_completed(240))
#     ok(!signalNotDisposed)
# 

# def test_SkipUntil_SomeData_Next():
#     var l, l_msgs, r, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
#     r_msgs = [on_next(150, 1), on_next(225, 99), on_completed(230)]
#     l = scheduler.create_hot_observable(l_msgs)
#     r = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal(on_next(230, 4), on_next(240, 5), on_completed(250))
# 

# def test_SkipUntil_SomeData_Error():
#     var ex, l, l_msgs, r, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     ex = 'ex'
#     l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
#     r_msgs = [on_next(150, 1), on_error(225, ex)]
#     l = scheduler.create_hot_observable(l_msgs)
#     r = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal(on_error(225, ex))
# 

# def test_SkipUntil_SomeData_Empty():
#     var l, l_msgs, r, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
#     r_msgs = [on_next(150, 1), on_completed(225)]
#     l = scheduler.create_hot_observable(l_msgs)
#     r = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal()
# 

# def test_SkipUntil_Never_Next():
#     var l, r, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     r_msgs = [on_next(150, 1), on_next(225, 2), on_completed(250)]
#     l = Observable.never()
#     r = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal()
# 

# def test_SkipUntil_Never_Error():
#     var ex, l, r, r_msgs, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     r_msgs = [on_next(150, 1), on_error(225, ex)]
#     l = Observable.never()
#     r = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal(on_error(225, ex))
# 

# def test_SkipUntil_SomeData_Never():
#     var l, l_msgs, r, results, scheduler
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
#     l = scheduler.create_hot_observable(l_msgs)
#     r = Observable.never()
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal()
# 

# def test_SkipUntil_Never_Empty():
#     var l, r, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     r_msgs = [on_next(150, 1), on_completed(225)]
#     l = Observable.never()
#     r = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal()
# 

# def test_SkipUntil_Never_Never():
#     var l, r, results, scheduler
#     scheduler = TestScheduler()
#     l = Observable.never()
#     r = Observable.never()
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal()
# 

# def test_SkipUntil_HasCompletedCausesDisposal():
#     var disposed, l, l_msgs, r, results, scheduler
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
#     disposed = false
#     l = scheduler.create_hot_observable(l_msgs)
#     r = Observable.create(function () {
#         return function () {
#             disposed = true
#         }
#     
#     results = scheduler.start(create)
#         return l.skipUntil(r)
#     
#     results.messages.assert_equal()
#     ok(disposed)
# 

# def test_Merge_Never2():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = Observable.never()
#     n2 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, n1, n2)
#     
#     results.messages.assert_equal()
# 

# def test_Merge_Never3():
#     var n1, n2, n3, results, scheduler
#     scheduler = TestScheduler()
#     n1 = Observable.never()
#     n2 = Observable.never()
#     n3 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, n1, n2, n3)
#     
#     results.messages.assert_equal()
# 

# def test_Merge_Empty2():
#     var e1, e2, results, scheduler
#     scheduler = TestScheduler()
#     e1 = Observable.empty()
#     e2 = Observable.empty()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, e1, e2)
#     
#     results.messages.assert_equal(on_completed(203))
# 

# def test_Merge_Empty3():
#     var e1, e2, e3, results, scheduler
#     scheduler = TestScheduler()
#     e1 = Observable.empty()
#     e2 = Observable.empty()
#     e3 = Observable.empty()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, e1, e2, e3)
#     
#     results.messages.assert_equal(on_completed(204))
# 

# def test_Merge_EmptyDelayed2_RightLast():
#     var e1, e2, l_msgs, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_completed(240)]
#     r_msgs = [on_next(150, 1), on_completed(250)]
#     e1 = scheduler.create_hot_observable(l_msgs)
#     e2 = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, e1, e2)
#     
#     results.messages.assert_equal(on_completed(250))
# 

# def test_Merge_EmptyDelayed2_LeftLast():
#     var e1, e2, l_msgs, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     l_msgs = [on_next(150, 1), on_completed(250)]
#     r_msgs = [on_next(150, 1), on_completed(240)]
#     e1 = scheduler.create_hot_observable(l_msgs)
#     e2 = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, e1, e2)
#     
#     results.messages.assert_equal(on_completed(250))
# 

# def test_Merge_EmptyDelayed3_MiddleLast():
#     var e1, e2, e3, msgs1, msgs2, msgs3, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(245)]
#     msgs2 = [on_next(150, 1), on_completed(250)]
#     msgs3 = [on_next(150, 1), on_completed(240)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     e3 = scheduler.create_hot_observable(msgs3)
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, e1, e2, e3)
#     
#     results.messages.assert_equal(on_completed(250))
# 

# def test_Merge_EmptyNever():
#     var e1, msgs1, n1, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(245)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     n1 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, e1, n1)
#     
#     results.messages.assert_equal()
# 

# def test_Merge_NeverEmpty():
#     var e1, msgs1, n1, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(245)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     n1 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, n1, e1)
#     
#     results.messages.assert_equal()
# 

# def test_Merge_ReturnNever():
#     var msgs1, n1, r1, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(245)]
#     r1 = scheduler.create_hot_observable(msgs1)
#     n1 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, r1, n1)
#     
#     results.messages.assert_equal(on_next(210, 2))
# 

# def test_Merge_NeverReturn():
#     var msgs1, n1, r1, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(245)]
#     r1 = scheduler.create_hot_observable(msgs1)
#     n1 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, n1, r1)
#     
#     results.messages.assert_equal(on_next(210, 2))
# 

# def test_Merge_ErrorNever():
#     var e1, ex, msgs1, n1, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     n1 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, e1, n1)
#     
#     results.messages.assert_equal(on_next(210, 2), on_error(245, ex))
# 

# def test_Merge_NeverError():
#     var e1, ex, msgs1, n1, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     n1 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, n1, e1)
#     
#     results.messages.assert_equal(on_next(210, 2), on_error(245, ex))
# 

# def test_Merge_EmptyReturn():
#     var e1, msgs1, msgs2, r1, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(245)]
#     msgs2 = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     r1 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, e1, r1)
#     
#     results.messages.assert_equal(on_next(210, 2), on_completed(250))
# 

# def test_Merge_ReturnEmpty():
#     var e1, msgs1, msgs2, r1, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(245)]
#     msgs2 = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     r1 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, r1, e1)
#     
#     results.messages.assert_equal(on_next(210, 2), on_completed(250))
# 

# def test_Merge_Lots2():
#     var i, msgs1, msgs2, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 4), on_next(230, 6), on_next(240, 8), on_completed(245)]
#     msgs2 = [on_next(150, 1), on_next(215, 3), on_next(225, 5), on_next(235, 7), on_next(245, 9), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, o1, o2)
#     .messages
#     equal(9, results.length)
#     for (i = 0 i < 8 i++) {
#         ok(results[i].value.kind === 'N' && results[i].time === 210 + i * 5 && results[i].value.value === i + 2)
#     }
#     ok(results[8].value.kind === 'C' && results[8].time === 250)
# 
# def test_Merge_Lots3():
#     var i, msgs1, msgs2, msgs3, o1, o2, o3, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(225, 5), on_next(240, 8), on_completed(245)]
#     msgs2 = [on_next(150, 1), on_next(215, 3), on_next(230, 6), on_next(245, 9), on_completed(250)]
#     msgs3 = [on_next(150, 1), on_next(220, 4), on_next(235, 7), on_completed(240)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     o3 = scheduler.create_hot_observable(msgs3)
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, o1, o2, o3)
#     .messages
#     equal(9, results.length)
#     for (i = 0 i < 8 i++) {
#         ok(results[i].value.kind === 'N' && results[i].time === 210 + i * 5 && results[i].value.value === i + 2)
#     }
#     ok(results[8].value.kind === 'C' && results[8].time === 250)
# 
# def test_Merge_ErrorLeft():
#     var ex, msgs1, msgs2, o1, o2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
#     msgs2 = [on_next(150, 1), on_next(215, 3), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, o1, o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(215, 3), on_error(245, ex))
# 
# def test_Merge_ErrorCausesDisposal():
#     var ex, msgs1, msgs2, o1, o2, results, scheduler, sourceNotDisposed
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_error(210, ex)]
#     msgs2 = [on_next(150, 1), on_next(220, 1), on_completed(250)]
#     sourceNotDisposed = false
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2).doAction(function () {
#         return sourceNotDisposed = true
#     
#     results = scheduler.start(create)
#         return Observable.merge(scheduler, o1, o2)
#     
#     results.messages.assert_equal(on_error(210, ex))
#     ok(!sourceNotDisposed)
# 
# def test_Merge_ObservableOfObservable_Data():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(300, scheduler.createColdObservable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.createColdObservable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_next(500, scheduler.createColdObservable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_next(120, 305), on_completed(150))), on_completed(600))
#     results = scheduler.start(create)
#         return xs.mergeObservable()
#     
#     results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 103), on_next(410, 201), on_next(420, 104), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_next(510, 105), on_next(510, 301), on_next(520, 106), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_next(620, 305), on_completed(650))
# 
# def test_Merge_ObservableOfObservable_Data_NonOverlapped():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(300, scheduler.createColdObservable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(400, scheduler.createColdObservable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_next(500, scheduler.createColdObservable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(50))), on_completed(600))
#     results = scheduler.start(create)
#         return xs.mergeObservable()
#     
#     results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_next(510, 301), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_completed(600))
# 
# def test_Merge_ObservableOfObservable_InnerThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(300, scheduler.createColdObservable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(400, scheduler.createColdObservable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_error(50, ex))), on_next(500, scheduler.createColdObservable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(50))), on_completed(600))
#     results = scheduler.start(create)
#         return xs.mergeObservable()
#     
#     results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(450, ex))
# 
# def test_Merge_ObservableOfObservable_OuterThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(300, scheduler.createColdObservable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(400, scheduler.createColdObservable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_error(500, ex))
#     results = scheduler.start(create)
#         return xs.mergeObservable()
#     
#     results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(500, ex))
# 
# def test_Switch_Data():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(300, scheduler.createColdObservable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.createColdObservable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_next(500, scheduler.createColdObservable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(150))), on_completed(600))
#     results = scheduler.start(create)
#         return xs.switchLatest()
#     
#     results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_next(510, 301), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_completed(650))
# 
# def test_Switch_InnerThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(300, scheduler.createColdObservable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.createColdObservable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_error(50, ex))), on_next(500, scheduler.createColdObservable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(150))), on_completed(600))
#     results = scheduler.start(create)
#         return xs.switchLatest()
#     
#     results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(450, ex))
# 
# def test_Switch_OuterThrows():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(300, scheduler.createColdObservable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.createColdObservable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_error(500, ex))
#     results = scheduler.start(create)
#         return xs.switchLatest()
#     
#     results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(500, ex))
# 
# def test_Switch_NoInner():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_completed(500))
#     results = scheduler.start(create)
#         return xs.switchLatest()
#     
#     results.messages.assert_equal(on_completed(500))
# 
# def test_Switch_InnerCompletes():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(300, scheduler.createColdObservable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_completed(540))
#     results = scheduler.start(create)
#         return xs.switchLatest()
#     
#     results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 103), on_next(420, 104), on_next(510, 105), on_next(520, 106), on_completed(540))
# 
# def test_Amb_Never2():
#     var l, r, results, scheduler
#     scheduler = TestScheduler()
#     l = Observable.never()
#     r = Observable.never()
#     results = scheduler.start(create)
#         return l.amb(r)
#     
#     results.messages.assert_equal()
# 
# def test_Amb_Never3():
#     var n1, n2, n3, results, scheduler
#     scheduler = TestScheduler()
#     n1 = Observable.never()
#     n2 = Observable.never()
#     n3 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.amb(n1, n2, n3)
#     
#     results.messages.assert_equal()
# 
# def test_Amb_NeverEmpty():
#     var e, n, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     r_msgs = [on_next(150, 1), on_completed(225)]
#     n = Observable.never()
#     e = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return n.amb(e)
#     
#     results.messages.assert_equal(on_completed(225))
# 
# def test_Amb_EmptyNever():
#     var e, n, r_msgs, results, scheduler
#     scheduler = TestScheduler()
#     r_msgs = [on_next(150, 1), on_completed(225)]
#     n = Observable.never()
#     e = scheduler.create_hot_observable(r_msgs)
#     results = scheduler.start(create)
#         return e.amb(n)
#     
#     results.messages.assert_equal(on_completed(225))
# 
# def test_Amb_RegularShouldDisposeLoser():
#     var msgs1, msgs2, o1, o2, results, scheduler, sourceNotDisposed
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(240)]
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
#     sourceNotDisposed = false
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2).doAction(function () {
#         return sourceNotDisposed = true
#     
#     results = scheduler.start(create)
#         return o1.amb(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_completed(240))
#     ok(!sourceNotDisposed)
# 
# def test_Amb_WinnerThrows():
#     var ex, msgs1, msgs2, o1, o2, results, scheduler, sourceNotDisposed
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex)]
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
#     sourceNotDisposed = false
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2).doAction(function () {
#         return sourceNotDisposed = true
#     
#     results = scheduler.start(create)
#         return o1.amb(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_error(220, ex))
#     ok(!sourceNotDisposed)
# 
# def test_Amb_LoserThrows():
#     var ex, msgs1, msgs2, o1, o2, results, scheduler, sourceNotDisposed
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(220, 2), on_error(230, ex)]
#     msgs2 = [on_next(150, 1), on_next(210, 3), on_completed(250)]
#     sourceNotDisposed = false
#     o1 = scheduler.create_hot_observable(msgs1).doAction(function () {
#         return sourceNotDisposed = true
#     
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.amb(o2)
#     
#     results.messages.assert_equal(on_next(210, 3), on_completed(250))
#     ok(!sourceNotDisposed)
# 
# def test_Amb_ThrowsBeforeElection():
#     var ex, msgs1, msgs2, o1, o2, results, scheduler, sourceNotDisposed
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_error(210, ex)]
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
#     sourceNotDisposed = false
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2).doAction(function () {
#         return sourceNotDisposed = true
#     
#     results = scheduler.start(create)
#         return o1.amb(o2)
#     
#     results.messages.assert_equal(on_error(210, ex))
#     ok(!sourceNotDisposed)
# 
# def test_Catch_NoErrors():
#     var msgs1, msgs2, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(230)]
#     msgs2 = [on_next(240, 5), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.catchException(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_completed(230))
# 
# def test_Catch_Never():
#     var msgs2, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs2 = [on_next(240, 5), on_completed(250)]
#     o1 = Observable.never()
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.catchException(o2)
#     
#     results.messages.assert_equal()
# 
# def test_Catch_Empty():
#     var msgs1, msgs2, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(230)]
#     msgs2 = [on_next(240, 5), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.catchException(o2)
#     
#     results.messages.assert_equal(on_completed(230))
# 
# def test_Catch_Return():
#     var msgs1, msgs2, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
#     msgs2 = [on_next(240, 5), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.catchException(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_completed(230))
# 
# def test_Catch_Error():
#     var ex, msgs1, msgs2, o1, o2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
#     msgs2 = [on_next(240, 5), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.catchException(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 5), on_completed(250))
# 
# def test_Catch_Error_Never():
#     var ex, msgs1, o1, o2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = Observable.never()
#     results = scheduler.start(create)
#         return o1.catchException(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3))
# 
# def test_Catch_Error_Error():
#     var ex, msgs1, msgs2, o1, o2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, 'ex1')]
#     msgs2 = [on_next(240, 4), on_error(250, ex)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.catchException(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_error(250, ex))
# 
# def test_Catch_Multiple():
#     var ex, msgs1, msgs2, msgs3, o1, o2, o3, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
#     msgs2 = [on_next(220, 3), on_error(225, ex)]
#     msgs3 = [on_next(230, 4), on_completed(235)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     o3 = scheduler.create_hot_observable(msgs3)
#     results = scheduler.start(create)
#         return Observable.catchException(o1, o2, o3)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(235))
# 
# def test_Catch_ErrorSpecific_Caught():
#     var ex, handlerCalled, msgs1, msgs2, o1, o2, results, scheduler
#     ex = 'ex'
#     handlerCalled = false
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
#     msgs2 = [on_next(240, 4), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.catchException(function (e) {
#             handlerCalled = true
#             return o2
#         
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_completed(250))
#     ok(handlerCalled)
# 
# def test_Catch_ErrorSpecific_CaughtImmediate():
#     var ex, handlerCalled, msgs2, o2, results, scheduler
#     ex = 'ex'
#     handlerCalled = false
#     scheduler = TestScheduler()
#     msgs2 = [on_next(240, 4), on_completed(250)]
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return Observable.throwException('ex').catchException(function (e) {
#             handlerCalled = true
#             return o2
#         
#     
#     results.messages.assert_equal(on_next(240, 4), on_completed(250))
#     ok(handlerCalled)
# 
# def test_Catch_HandlerThrows():
#     var ex, ex2, handlerCalled, msgs1, o1, results, scheduler
#     ex = 'ex'
#     ex2 = 'ex2'
#     handlerCalled = false
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     results = scheduler.start(create)
#         return o1.catchException(function (e) {
#             handlerCalled = true
#             throw ex2
#         
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_error(230, ex2))
#     ok(handlerCalled)
# 
# def test_Catch_Nested_OuterCatches():
#     var ex, firstHandlerCalled, msgs1, msgs2, msgs3, o1, o2, o3, results, scheduler, secondHandlerCalled
#     ex = 'ex'
#     firstHandlerCalled = false
#     secondHandlerCalled = false
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
#     msgs2 = [on_next(220, 3), on_completed(225)]
#     msgs3 = [on_next(220, 4), on_completed(225)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     o3 = scheduler.create_hot_observable(msgs3)
#     results = scheduler.start(create)
#         return o1.catchException(function (e) {
#             firstHandlerCalled = true
#             return o2
#         .catchException(function (e) {
#             secondHandlerCalled = true
#             return o3
#         
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_completed(225))
#     ok(firstHandlerCalled)
#     ok(!secondHandlerCalled)
# 
# def test_Catch_ThrowFromNestedCatch():
#     var ex, ex2, firstHandlerCalled, msgs1, msgs2, msgs3, o1, o2, o3, results, scheduler, secondHandlerCalled
#     ex = 'ex'
#     ex2 = 'ex'
#     firstHandlerCalled = false
#     secondHandlerCalled = false
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
#     msgs2 = [on_next(220, 3), on_error(225, ex2)]
#     msgs3 = [on_next(230, 4), on_completed(235)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     o3 = scheduler.create_hot_observable(msgs3)
#     results = scheduler.start(create)
#         return o1.catchException(function (e) {
#             firstHandlerCalled = true
#             equal(e, ex)
#             return o2
#         .catchException(function (e) {
#             secondHandlerCalled = true
#             equal(e, ex2)
#             return o3
#         
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(235))
#     ok(firstHandlerCalled)
#     ok(secondHandlerCalled)
# 
# def test_On_errorResumeNext_NoErrors():
#     var msgs1, msgs2, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(230)]
#     msgs2 = [on_next(240, 4), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.on_errorResumeNext(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_completed(250))
# 
# def test_On_errorResumeNext_Error():
#     var msgs1, msgs2, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, 'ex')]
#     msgs2 = [on_next(240, 4), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.on_errorResumeNext(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_completed(250))
# 
# def test_On_errorResumeNext_ErrorMultiple():
#     var msgs1, msgs2, msgs3, o1, o2, o3, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, 'ex')]
#     msgs2 = [on_next(230, 4), on_error(240, 'ex')]
#     msgs3 = [on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     o3 = scheduler.create_hot_observable(msgs3)
#     results = scheduler.start(create)
#         return Observable.on_errorResumeNext(o1, o2, o3)
#     
#     results.messages.assert_equal(on_next(210, 2), on_next(230, 4), on_completed(250))
# 
# def test_On_errorResumeNext_EmptyReturnThrowAndMore():
#     var msgs1, msgs2, msgs3, msgs4, msgs5, o1, o2, o3, o4, o5, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(205)]
#     msgs2 = [on_next(215, 2), on_completed(220)]
#     msgs3 = [on_next(225, 3), on_next(230, 4), on_completed(235)]
#     msgs4 = [on_error(240, 'ex')]
#     msgs5 = [on_next(245, 5), on_completed(250)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     o3 = scheduler.create_hot_observable(msgs3)
#     o4 = scheduler.create_hot_observable(msgs4)
#     o5 = scheduler.create_hot_observable(msgs5)
#     results = scheduler.start(create)
#         return Observable.on_errorResumeNext(o1, o2, o3, o4, o5)
#     
#     results.messages.assert_equal(on_next(215, 2), on_next(225, 3), on_next(230, 4), on_next(245, 5), on_completed(250))
# 
# def test_On_errorResumeNext_EmptyReturnThrowAndMore():
#     var ex, msgs1, msgs2, o1, o2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(220)]
#     msgs2 = [on_error(230, ex)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return o1.on_errorResumeNext(o2)
#     
#     results.messages.assert_equal(on_next(210, 2), on_completed(230))
# 
# def test_On_errorResumeNext_SingleSourceThrows():
#     var ex, msgs1, o1, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_error(230, ex)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     results = scheduler.start(create)
#         return Observable.on_errorResumeNext(o1)
#     
#     results.messages.assert_equal(on_completed(230))
# 
# def test_On_errorResumeNext_EndWithNever():
#     var msgs1, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(220)]
#     o1 = scheduler.create_hot_observable(msgs1)
#     o2 = Observable.never()
#     results = scheduler.start(create)
#         return Observable.on_errorResumeNext(o1, o2)
#     
#     results.messages.assert_equal(on_next(210, 2))
# 
# def test_On_errorResumeNext_StartWithNever():
#     var msgs1, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(220)]
#     o1 = Observable.never()
#     o2 = scheduler.create_hot_observable(msgs1)
#     results = scheduler.start(create)
#         return Observable.on_errorResumeNext(o1, o2)
#     
#     results.messages.assert_equal()
# 
# def test_Zip_NeverNever():
#     var o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     o1 = Observable.never()
#     o2 = Observable.never()
#     results = scheduler.start(create)
#         return o1.zip(o2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_Zip_NeverEmpty():
#     var msgs, o1, o2, results, scheduler
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(210)]
#     o1 = Observable.never()
#     o2 = scheduler.create_hot_observable(msgs)
#     results = scheduler.start(create)
#         return o1.zip(o2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_Zip_EmptyEmpty():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(210)]
#     msgs2 = [on_next(150, 1), on_completed(210)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(210))
# 
# def test_Zip_EmptyNonEmpty():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(210)]
#     msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(215))
# 
# def test_Zip_NonEmptyEmpty():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(210)]
#     msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.zip(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(215))
# 
# def test_Zip_NeverNonEmpty():
#     var e1, e2, msgs, results, scheduler
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     e1 = scheduler.create_hot_observable(msgs)
#     e2 = Observable.never()
#     results = scheduler.start(create)
#         return e2.zip(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_Zip_NonEmptyNever():
#     var e1, e2, msgs, results, scheduler
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     e1 = scheduler.create_hot_observable(msgs)
#     e2 = Observable.never()
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_Zip_NonEmptyNonEmpty():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(220, 2 + 3), on_completed(240))
# 
# def test_Zip_EmptyError():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Zip_ErrorEmpty():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.zip(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Zip_NeverError():
#     var e1, e2, ex, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = Observable.never()
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Zip_ErrorNever():
#     var e1, e2, ex, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = Observable.never()
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.zip(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Zip_ErrorError():
#     var e1, e2, ex1, ex2, msgs1, msgs2, results, scheduler
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_error(230, ex1)]
#     msgs2 = [on_next(150, 1), on_error(220, ex2)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.zip(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex2))
# 
# def test_Zip_SomeError():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Zip_ErrorSome():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.zip(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Zip_SomeDataAsymmetric1():
#     var e1, e2, i, len, msgs1, msgs2, results, scheduler, sum, time
#     scheduler = TestScheduler()
#     msgs1 = (function () {
#         var _results
#         _results = []
#         for (i = 0 i < 5 i++) {
#             _results.push(on_next(205 + i * 5, i))
#         }
#         return _results
#     ()
#     msgs2 = (function () {
#         var _results
#         _results = []
#         for (i = 0 i < 10 i++) {
#             _results.push(on_next(205 + i * 8, i))
#         }
#         return _results
#     ()
#     len = Math.min(msgs1.length, msgs2.length)
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     .messages
#     equal(len, results.length)
#     for (i = 0 i < len i++) {
#         sum = msgs1[i].value.value + msgs2[i].value.value
#         time = Math.max(msgs1[i].time, msgs2[i].time)
#         ok(results[i].value.kind === 'N' && results[i].time === time && results[i].value.value === sum)
#     }
# 
# def test_Zip_SomeDataAsymmetric2():
#     var e1, e2, i, len, msgs1, msgs2, results, scheduler, sum, time
#     scheduler = TestScheduler()
#     msgs1 = (function () {
#         var _results
#         _results = []
#         for (i = 0 i < 10 i++) {
#             _results.push(on_next(205 + i * 5, i))
#         }
#         return _results
#     ()
#     msgs2 = (function () {
#         var _results
#         _results = []
#         for (i = 0 i < 5 i++) {
#             _results.push(on_next(205 + i * 8, i))
#         }
#         return _results
#     ()
#     len = Math.min(msgs1.length, msgs2.length)
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     .messages
#     equal(len, results.length)
#     for (i = 0 i < len i++) {
#         sum = msgs1[i].value.value + msgs2[i].value.value
#         time = Math.max(msgs1[i].time, msgs2[i].time)
#         ok(results[i].value.kind === 'N' && results[i].time === time && results[i].value.value === sum)
#     }
# 
# def test_Zip_SomeDataSymmetric():
#     var e1, e2, i, len, msgs1, msgs2, results, scheduler, sum, time
#     scheduler = TestScheduler()
#     msgs1 = (function () {
#         var _results
#         _results = []
#         for (i = 0 i < 10 i++) {
#             _results.push(on_next(205 + i * 5, i))
#         }
#         return _results
#     ()
#     msgs2 = (function () {
#         var _results
#         _results = []
#         for (i = 0 i < 10 i++) {
#             _results.push(on_next(205 + i * 8, i))
#         }
#         return _results
#     ()
#     len = Math.min(msgs1.length, msgs2.length)
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             return x + y
#         
#     .messages
#     equal(len, results.length)
#     for (i = 0 i < len i++) {
#         sum = msgs1[i].value.value + msgs2[i].value.value
#         time = Math.max(msgs1[i].time, msgs2[i].time)
#         ok(results[i].value.kind === 'N' && results[i].time === time && results[i].value.value === sum)
#     }
# 
# def test_Zip_SelectorThrows():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(240)]
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_next(230, 5), on_completed(250)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.zip(e2, function (x, y) {
#             if (y === 5) {
#                 throw ex
#             } else {
#                 return x + y
#             }
#         
#     
#     results.messages.assert_equal(on_next(220, 2 + 3), on_error(230, ex))
# 
# def test_CombineLatest_NeverNever():
#     var e1, e2, results, scheduler
#     scheduler = TestScheduler()
#     e1 = Observable.never()
#     e2 = Observable.never()
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_CombineLatest_NeverEmpty():
#     var e1, e2, msgs, results, scheduler
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(210)]
#     e1 = Observable.never()
#     e2 = scheduler.create_hot_observable(msgs)
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_CombineLatest_EmptyNever():
#     var e1, e2, msgs, results, scheduler
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(210)]
#     e1 = Observable.never()
#     e2 = scheduler.create_hot_observable(msgs)
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_CombineLatest_EmptyEmpty():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(210)]
#     msgs2 = [on_next(150, 1), on_completed(210)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(210))
# 
# def test_CombineLatest_EmptyReturn():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(210)]
#     msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(215))
# 
# def test_CombineLatest_ReturnEmpty():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(210)]
#     msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(215))
# 
# def test_CombineLatest_NeverReturn():
#     var e1, e2, msgs, results, scheduler
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     e1 = scheduler.create_hot_observable(msgs)
#     e2 = Observable.never()
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_CombineLatest_ReturnNever():
#     var e1, e2, msgs, results, scheduler
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(215, 2), on_completed(210)]
#     e1 = scheduler.create_hot_observable(msgs)
#     e2 = Observable.never()
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
# 
# def test_CombineLatest_ReturnReturn():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(220, 2 + 3), on_completed(240))
# 
# def test_CombineLatest_EmptyError():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_CombineLatest_ErrorEmpty():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_CombineLatest_ReturnThrow():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_CombineLatest_ThrowReturn():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_CombineLatest_ThrowThrow():
#     var e1, e2, ex1, ex2, msgs1, msgs2, results, scheduler
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_error(220, ex1)]
#     msgs2 = [on_next(150, 1), on_error(230, ex2)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex1))
# 
# def test_CombineLatest_ErrorThrow():
#     var e1, e2, ex1, ex2, msgs1, msgs2, results, scheduler
#     ex1 = 'ex1'
#     ex2 = 'ex2'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex1)]
#     msgs2 = [on_next(150, 1), on_error(230, ex2)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex1));
# ;
# def test_CombineLatest_ThrowError():
#     var e1, e2, ex1, ex2, msgs1, msgs2, results, scheduler;
#     ex1 = 'ex1';
#     ex2 = 'ex2';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex1)];
#     msgs2 = [on_next(150, 1), on_error(230, ex2)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex1));
# ;
# def test_CombineLatest_NeverThrow():
#     var e1, e2, ex, msgs, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs = [on_next(150, 1), on_error(220, ex)];
#     e1 = Observable.never();
#     e2 = scheduler.create_hot_observable(msgs);
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex));
# ;
# def test_CombineLatest_ThrowNever():
#     var e1, e2, ex, msgs, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs = [on_next(150, 1), on_error(220, ex)];
#     e1 = Observable.never();
#     e2 = scheduler.create_hot_observable(msgs);
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex));
# ;
# def test_CombineLatest_SomeThrow():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_error(220, ex)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex));
# ;
# def test_CombineLatest_ThrowSome():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_error(220, ex)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex));
# ;
# def test_CombineLatest_ThrowAfterCompleteLeft():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(220)];
#     msgs2 = [on_next(150, 1), on_error(230, ex)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(230, ex));
# ;
# def test_CombineLatest_ThrowAfterCompleteRight():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(220)];
#     msgs2 = [on_next(150, 1), on_error(230, ex)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(230, ex));
# ;
# def test_CombineLatest_InterleavedWithTail():
#     var e1, e2, msgs1, msgs2, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_next(230, 5), on_next(235, 6), on_next(240, 7), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_next(220, 2 + 3), on_next(225, 3 + 4), on_next(230, 4 + 5), on_next(235, 4 + 6), on_next(240, 4 + 7), on_completed(250));
# ;
# def test_CombineLatest_Consecutive():
#     var e1, e2, msgs1, msgs2, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_next(235, 4 + 6), on_next(240, 4 + 7), on_completed(250));
# ;
# def test_CombineLatest_ConsecutiveEndWithErrorLeft():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_error(230, ex)];
#     msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(230, ex));
# ;
# def test_CombineLatest_ConsecutiveEndWithErrorRight():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_error(245, ex)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e2.combineLatest(e1, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_next(235, 4 + 6), on_next(240, 4 + 7), on_error(245, ex));
# ;
# def test_CombineLatest_SelectorThrows():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.combineLatest(e2, function () {
#             throw ex;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex));
# ;
# def test_Concat_EmptyEmpty():
#     var e1, e2, msgs1, msgs2, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_completed(250));
# ;
# def test_Concat_EmptyNever():
#     var e1, e2, msgs1, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_completed(230)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = Observable.never();
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal();
# ;
# def test_Concat_NeverEmpty():
#     var e1, e2, msgs1, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_completed(230)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = Observable.never();
#     results = scheduler.start(create)
#         return e2.concat(e1);
#     ;
#     results.messages.assert_equal();
# ;
# def test_Concat_NeverNever():
#     var e1, e2, results, scheduler;
#     scheduler = TestScheduler();
#     e1 = Observable.never();
#     e2 = Observable.never();
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal();
# ;
# def test_Concat_EmptyThrow():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_error(250, ex)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_error(250, ex));
# ;
# def test_Concat_ThrowEmpty():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_error(230, ex)];
#     msgs2 = [on_next(150, 1), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_error(230, ex));
# ;
# def test_Concat_ThrowThrow():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_error(230, ex)];
#     msgs2 = [on_next(150, 1), on_error(250, 'ex2')];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_error(230, ex));
# ;
# def test_Concat_ReturnEmpty():
#     var e1, e2, msgs1, msgs2, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_next(210, 2), on_completed(250));
# ;
# def test_Concat_EmptyReturn():
#     var e1, e2, msgs1, msgs2, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_next(240, 2), on_completed(250));
# ;
# def test_Concat_ReturnNever():
#     var e1, e2, msgs1, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = Observable.never();
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_next(210, 2));
# ;
# def test_Concat_NeverReturn():
#     var e1, e2, msgs1, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = Observable.never();
#     results = scheduler.start(create)
#         return e2.concat(e1);
#     ;
#     results.messages.assert_equal();
# ;
# def test_Concat_ReturnReturn():
#     var e1, e2, msgs1, msgs2, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_next(240, 3), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_next(220, 2), on_next(240, 3), on_completed(250));
# ;
# def test_Concat_ThrowReturn():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_error(230, ex)];
#     msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_error(230, ex));
# ;
# def test_Concat_ReturnThrow():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)];
#     msgs2 = [on_next(150, 1), on_error(250, ex)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_next(220, 2), on_error(250, ex));
# ;
# def test_Concat_SomeDataSomeData():
#     var e1, e2, msgs1, msgs2, results, scheduler;
#     scheduler = TestScheduler();
#     msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(225)];
#     msgs2 = [on_next(150, 1), on_next(230, 4), on_next(240, 5), on_completed(250)];
#     e1 = scheduler.create_hot_observable(msgs1);
#     e2 = scheduler.create_hot_observable(msgs2);
#     results = scheduler.start(create)
#         return e1.concat(e2);
#     ;
#     results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250));
# ;
# def test_MergeConcat_Basic():
#     var results, scheduler, xs;
#     scheduler = TestScheduler();
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.createColdObservable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.createColdObservable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.createColdObservable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.createColdObservable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400));
#     results = scheduler.start(create)
#         return xs.merge(2);
#     ;
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_next(670, 9), on_next(700, 10), on_completed(760));
#     xs.subscriptions.assert_equal(subscribe(200, 760));
# ;
# def test_MergeConcat_Basic_Long():
#     var results, scheduler, xs;
#     scheduler = TestScheduler();
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.createColdObservable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.createColdObservable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.createColdObservable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.createColdObservable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400));
#     results = scheduler.start(create)
#         return xs.merge(2);
#     ;
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_next(690, 9), on_next(720, 10), on_completed(780));
#     xs.subscriptions.assert_equal(subscribe(200, 780));
# ;
# def test_MergeConcat_Basic_Wide():
#     var results, scheduler, xs;
#     scheduler = TestScheduler();
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.createColdObservable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.createColdObservable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.createColdObservable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(420, scheduler.createColdObservable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(450));
#     results = scheduler.start(create)
#         return xs.merge(3);
#     ;
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(280, 6), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 7), on_next(380, 8), on_next(630, 9), on_next(660, 10), on_completed(720));
#     xs.subscriptions.assert_equal(subscribe(200, 720));
# ;
# def test_MergeConcat_Basic_Late():
#     var results, scheduler, xs;
#     scheduler = TestScheduler();
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.createColdObservable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.createColdObservable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.createColdObservable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(420, scheduler.createColdObservable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(750));
#     results = scheduler.start(create)
#         return xs.merge(3);
#     ;
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(280, 6), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 7), on_next(380, 8), on_next(630, 9), on_next(660, 10), on_completed(750));
#     xs.subscriptions.assert_equal(subscribe(200, 750));
# ;
# def test_MergeConcat_Disposed():
#     var results, scheduler, xs;
#     scheduler = TestScheduler();
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.createColdObservable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.createColdObservable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.createColdObservable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.createColdObservable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400));
#     results = scheduler.startWithDispose(function () {
#         return xs.merge(2);
#     }, 450);
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7));
#     xs.subscriptions.assert_equal(subscribe(200, 450));
# ;
# def test_MergeConcat_OuterError():
#     var ex, results, scheduler, xs;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.createColdObservable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.createColdObservable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.createColdObservable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.createColdObservable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_error(400, ex));
#     results = scheduler.start(create)
#         return xs.merge(2);
#     ;
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_error(400, ex));
#     xs.subscriptions.assert_equal(subscribe(200, 400));
# ;
# def test_MergeConcat_InnerError():
#     var ex, results, scheduler, xs;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.createColdObservable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.createColdObservable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.createColdObservable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_error(140, ex))), on_next(320, scheduler.createColdObservable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400));
#     results = scheduler.start(create)
#         return xs.merge(2);
#     ;
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_error(490, ex));
#     xs.subscriptions.assert_equal(subscribe(200, 490));
# ;
# def test_ZipWithEnumerable_NeverEmpty():
#     var n1, n2, results, scheduler;
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1));
#     n2 = [];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal();
#     n1.subscriptions.assert_equal(subscribe(200, 1000));
# ;
# def test_ZipWithEnumerable_EmptyEmpty():
#     var n1, n2, results, scheduler;
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210));
#     n2 = [];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_completed(210));
#     n1.subscriptions.assert_equal(subscribe(200, 210));
# ;
# def test_ZipWithEnumerable_EmptyNonEmpty():
#     var n1, n2, results, scheduler;
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210));
#     n2 = [2];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_completed(210));
#     n1.subscriptions.assert_equal(subscribe(200, 210));
# ;
# def test_ZipWithEnumerable_NonEmptyEmpty():
#     var n1, n2, results, scheduler;
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_completed(220));
#     n2 = [];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_completed(215));
#     n1.subscriptions.assert_equal(subscribe(200, 215));
# ;
# def test_ZipWithEnumerable_NeverNonEmpty():
#     var n1, n2, results, scheduler;
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1));
#     n2 = [2];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal();
#     n1.subscriptions.assert_equal(subscribe(200, 1000));
# ;
# def test_ZipWithEnumerable_NonEmptyNonEmpty():
#     var n1, n2, results, scheduler;
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_completed(230));
#     n2 = [3];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_next(215, 2 + 3), on_completed(230));
#     n1.subscriptions.assert_equal(subscribe(200, 230));
# ;
# def test_ZipWithEnumerable_ErrorEmpty():
#     var ex, n1, n2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex));
#     n2 = [];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex));
#     n1.subscriptions.assert_equal(subscribe(200, 220));
# ;

# def test_ZipWithEnumerable_ErrorSome():
#     var ex, n1, n2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex));
#     n2 = [2];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_error(220, ex));
#     n1.subscriptions.assert_equal(subscribe(200, 220));
# ;
# def test_ZipWithEnumerable_SomeDataBothSides():
#     var n1, n2, results, scheduler;
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5));
#     n2 = [5, 4, 3, 2];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_next(210, 7), on_next(220, 7), on_next(230, 7), on_next(240, 7));
#     n1.subscriptions.assert_equal(subscribe(200, 1000));
# ;
# def test_ZipWithEnumerable_SelectorThrows():
#     var ex, n1, n2, results, scheduler;
#     ex = 'ex';
#     scheduler = TestScheduler();
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(240));
#     n2 = [3, 5];
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             if (y === 5) {
#                 throw ex;
#             }
#             return x + y;
#         ;
#     ;
#     results.messages.assert_equal(on_next(215, 2 + 3), on_error(225, ex));
#     n1.subscriptions.assert_equal(subscribe(200, 225));
# ;

# test("Rx.Observable.catchException() does not lose subscription to underlying observable", 12, function () {
#     var subscribes = 0,
#             unsubscribes = 0,
#             tracer = Rx.Observable.create(function (observer) { ++subscribes; return function () { ++unsubscribes; }; ,
#             s;

#     // Try it without catchException()
#     s = tracer.subscribe();
#     strictEqual(subscribes, 1, "1 subscribes");
#     strictEqual(unsubscribes, 0, "0 unsubscribes");
#     s.dispose();
#     strictEqual(subscribes, 1, "After dispose: 1 subscribes");
#     strictEqual(unsubscribes, 1, "After dispose: 1 unsubscribes");

#     // Now try again with catchException(Observable):
#     subscribes = unsubscribes = 0;
#     s = tracer.catchException(Rx.Observable.never()).subscribe();
#     strictEqual(subscribes, 1, "catchException(Observable): 1 subscribes");
#     strictEqual(unsubscribes, 0, "catchException(Observable): 0 unsubscribes");
#     s.dispose();
#     strictEqual(subscribes, 1, "catchException(Observable): After dispose: 1 subscribes");
#     strictEqual(unsubscribes, 1, "catchException(Observable): After dispose: 1 unsubscribes");

#     // And now try again with catchException(function()):
#     subscribes = unsubscribes = 0;
#     s = tracer.catchException(function () { return Rx.Observable.never(); .subscribe();
#     strictEqual(subscribes, 1, "catchException(function): 1 subscribes");
#     strictEqual(unsubscribes, 0, "catchException(function): 0 unsubscribes");
#     s.dispose();
#     strictEqual(subscribes, 1, "catchException(function): After dispose: 1 subscribes");
#     strictEqual(unsubscribes, 1, "catchException(function): After dispose: 1 unsubscribes"); // this one FAILS (unsubscribes is 0)
# ;

# // must call `QUnit.start()` if using QUnit < 1.3.0 with Node.js or any
# // version of QUnit with Narwhal, Rhino, or RingoJS

# }(typeof global == 'object' && global || this))*/