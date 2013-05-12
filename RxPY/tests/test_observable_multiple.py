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

def test_Take_until_Preempt_BeforeFirstProduced():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
    r_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(210))

def test_take_until_preempt_beforefirstproduced_remain_silent_and_proper_disposed():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_error(215, 'ex'), on_completed(240)]
    r_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
    source_not_disposed = False

    def action():
        nonlocal source_not_disposed

        source_not_disposed = True
    l = scheduler.create_hot_observable(l_msgs).do_action(on_next=action)
    
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_completed(210))
    assert(not source_not_disposed)

def test_take_until_nopreempt_afterlastproduced_proper_disposed_signal():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
    r_msgs = [on_next(150, 1), on_next(250, 2), on_completed(260)]
    signal_not_disposed = False
    l = scheduler.create_hot_observable(l_msgs)

    def action():
        nonlocal signal_not_disposed
        signal_not_disposed = True
    r = scheduler.create_hot_observable(r_msgs).do_action(on_next=action)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)        
    results.messages.assert_equal(on_next(230, 2), on_completed(240))
    assert(not signal_not_disposed)

def test_skip_until_somedata_next():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_next(225, 99), on_completed(230)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(230, 4), on_next(240, 5), on_completed(250))

def test_skip_until_somedata_error():
    scheduler = TestScheduler()
    ex = 'ex'
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_error(225, ex)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(225, ex))

def test_skip_until_somedata_empty():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_completed(225)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_never_next():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_next(225, 2), on_completed(250)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_never_error():
    ex = 'ex'
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_error(225, ex)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(225, ex))

def test_skip_until_somedata_never():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    l = scheduler.create_hot_observable(l_msgs)
    r = Observable.never()

    def create():
        return l.skip_until(r)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_never_empty():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_completed(225)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_never_never():
    scheduler = TestScheduler()
    l = Observable.never()
    r = Observable.never()
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_has_completed_causes_disposal():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    disposed = False
    l = scheduler.create_hot_observable(l_msgs)
    
    def subscribe(observer):
        nonlocal disposed
        disposed = True
    
    r = Observable(subscribe)
        
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()
    assert(disposed)

def test_merge_never2():
    scheduler = TestScheduler()
    n1 = Observable.never()
    n2 = Observable.never()
    
    def create():
        return Observable.merge(scheduler, n1, n2)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_merge_never3():
    scheduler = TestScheduler()
    n1 = Observable.never()
    n2 = Observable.never()
    n3 = Observable.never()
    
    def create():
        return Observable.merge(scheduler, n1, n2, n3)
    
    results = scheduler.start(create)    
    results.messages.assert_equal()

def test_merge_empty2():
    scheduler = TestScheduler()
    e1 = Observable.empty()
    e2 = Observable.empty()
    
    def create():
        return Observable.merge(scheduler, e1, e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(203))


def test_merge_empty3():
    scheduler = TestScheduler()
    e1 = Observable.empty()
    e2 = Observable.empty()
    e3 = Observable.empty()

    def create():
        return Observable.merge(scheduler, e1, e2, e3)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(204))

def test_merge_empty_delayed2_right_last():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_completed(240)]
    r_msgs = [on_next(150, 1), on_completed(250)]
    e1 = scheduler.create_hot_observable(l_msgs)
    e2 = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return Observable.merge(scheduler, e1, e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(250))

def test_merge_empty_delayed2_left_last():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_completed(250)]
    r_msgs = [on_next(150, 1), on_completed(240)]
    e1 = scheduler.create_hot_observable(l_msgs)
    e2 = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return Observable.merge(scheduler, e1, e2)
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(250))

def test_merge_empty_delayed3_middle_last():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(245)]
    msgs2 = [on_next(150, 1), on_completed(250)]
    msgs3 = [on_next(150, 1), on_completed(240)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    e3 = scheduler.create_hot_observable(msgs3)

    def create():
       return Observable.merge(scheduler, e1, e2, e3)

    results = scheduler.start(create)    
    results.messages.assert_equal(on_completed(250))

def test_merge_empty_never():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(245)]
    e1 = scheduler.create_hot_observable(msgs1)
    n1 = Observable.never()
    
    def create():
       return Observable.merge(scheduler, e1, n1)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_merge_never_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(245)]
    e1 = scheduler.create_hot_observable(msgs1)
    n1 = Observable.never()
    
    def create():
        return Observable.merge(scheduler, n1, e1)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_merge_return_never():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(245)]
    r1 = scheduler.create_hot_observable(msgs1)
    n1 = Observable.never()
    
    def create():
        return Observable.merge(scheduler, r1, n1)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2))

def test_merge_never_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(245)]
    r1 = scheduler.create_hot_observable(msgs1)
    n1 = Observable.never()

    def create():
        return Observable.merge(scheduler, n1, r1)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2))

def test_merge_error_never():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    n1 = Observable.never()

    def create():
        return Observable.merge(scheduler, e1, n1)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_error(245, ex))

def test_merge_never_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    n1 = Observable.never()
    
    def create():
        return Observable.merge(scheduler, n1, e1)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_error(245, ex))

def test_merge_empty_eeturn():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(245)]
    msgs2 = [on_next(150, 1), on_next(210, 2), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    r1 = scheduler.create_hot_observable(msgs2)

    def create():
        return Observable.merge(scheduler, e1, r1)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_completed(250))

def test_merge_return_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(245)]
    msgs2 = [on_next(150, 1), on_next(210, 2), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    r1 = scheduler.create_hot_observable(msgs2)

    def create():
        return Observable.merge(scheduler, r1, e1)

    results = scheduler.start(create)    
    results.messages.assert_equal(on_next(210, 2), on_completed(250))

def test_merge_lots2():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 4), on_next(230, 6), on_next(240, 8), on_completed(245)]
    msgs2 = [on_next(150, 1), on_next(215, 3), on_next(225, 5), on_next(235, 7), on_next(245, 9), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return Observable.merge(scheduler, o1, o2)
    
    results = scheduler.start(create).messages
    assert(len(results) == 9)
    for i, result in enumerate(results[:-1]):
        assert(result.value.kind == 'N')
        assert(result.time == 210 + i * 5)
        assert(result.value.value == i + 2)
    
    assert(results[8].value.kind == 'C' and results[8].time == 250)

def test_merge_lots3():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(225, 5), on_next(240, 8), on_completed(245)]
    msgs2 = [on_next(150, 1), on_next(215, 3), on_next(230, 6), on_next(245, 9), on_completed(250)]
    msgs3 = [on_next(150, 1), on_next(220, 4), on_next(235, 7), on_completed(240)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    o3 = scheduler.create_hot_observable(msgs3)
    
    def create():
        return Observable.merge(scheduler, o1, o2, o3)
    
    results = scheduler.start(create).messages
    assert(len(results) == 9)
    for i, result in enumerate(results[:-1]):
        assert(results[i].value.kind == 'N' and results[i].time == 210 + i * 5 and results[i].value.value == i + 2)
    
    assert(results[8].value.kind == 'C' and results[8].time == 250)

def test_merge_error_left():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(245, ex)]
    msgs2 = [on_next(150, 1), on_next(215, 3), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return Observable.merge(scheduler, o1, o2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(215, 3), on_error(245, ex))

def test_merge_error_causes_disposal():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(210, ex)]
    msgs2 = [on_next(150, 1), on_next(220, 1), on_completed(250)]
    source_not_disposed = False
    o1 = scheduler.create_hot_observable(msgs1)
    
    def action():
        nonlocal source_not_disposed
        source_not_disposed = True
    
    o2 = scheduler.create_hot_observable(msgs2).do_action(on_next=action)
    
    def create():
        return Observable.merge(scheduler, o1, o2)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(210, ex))
    assert(not source_not_disposed)

def test_merge_observable_of_observable_data():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_next(120, 305), on_completed(150))), on_completed(600))
    
    def create():
        return xs.merge_observable()
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 103), on_next(410, 201), on_next(420, 104), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_next(510, 105), on_next(510, 301), on_next(520, 106), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_next(620, 305), on_completed(650))

def test_merge_observable_of_observable_data_non_overlapped():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(50))), on_completed(600))
    
    def create():
        return xs.merge_observable()

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_next(510, 301), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_completed(600))

def test_merge_observable_of_observable_inner_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_error(50, ex))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(50))), on_completed(600))

    def create():
        return xs.merge_observable()

    results = scheduler.start(create)    
    results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(450, ex))

def test_merge_observable_of_observable_outer_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_error(500, ex))
    
    def create():
        return xs.merge_observable()
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(500, ex))

def test_switch_data():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(150))), on_completed(600))
    
    def create():
        return xs.switch_latest()
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_next(510, 301), on_next(520, 302), on_next(530, 303), on_next(540, 304), on_completed(650))

def test_switch_inner_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_error(50, ex))), on_next(500, scheduler.create_cold_observable(on_next(10, 301), on_next(20, 302), on_next(30, 303), on_next(40, 304), on_completed(150))), on_completed(600))
    
    def create():
        return xs.switch_latest()
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(450, ex))

def test_switch_outer_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_next(400, scheduler.create_cold_observable(on_next(10, 201), on_next(20, 202), on_next(30, 203), on_next(40, 204), on_completed(50))), on_error(500, ex))
    
    def create():
        return xs.switch_latest()
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 201), on_next(420, 202), on_next(430, 203), on_next(440, 204), on_error(500, ex))

def test_switch_no_inner():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_completed(500))
    
    def create():
        return xs.switch_latest()
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(500))

def test_switch_inner_completes():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(300, scheduler.create_cold_observable(on_next(10, 101), on_next(20, 102), on_next(110, 103), on_next(120, 104), on_next(210, 105), on_next(220, 106), on_completed(230))), on_completed(540))
    
    def create():
        return xs.switch_latest()

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(310, 101), on_next(320, 102), on_next(410, 103), on_next(420, 104), on_next(510, 105), on_next(520, 106), on_completed(540))

def test_amb_never2():
    scheduler = TestScheduler()
    l = Observable.never()
    r = Observable.never()

    def create():
        return l.amb(r)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_amb_never3():
    scheduler = TestScheduler()
    n1 = Observable.never()
    n2 = Observable.never()
    n3 = Observable.never()

    def create():
        return Observable.amb(n1, n2, n3)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_amb_never_empty():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_completed(225)]
    n = Observable.never()
    e = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return n.amb(e)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(225))

def test_amb_empty_never():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_completed(225)]
    n = Observable.never()
    e = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return e.amb(n)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(225))

def test_amb_regular_should_dispose_loser():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(240)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
    source_not_disposed = False
    o1 = scheduler.create_hot_observable(msgs1)

    def action():
        nonlocal source_not_disposed
        source_not_disposed = True

    o2 = scheduler.create_hot_observable(msgs2).do_action(on_next=action)
    
    def create():
        return o1.amb(o2)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, 2), on_completed(240))
    assert(not source_not_disposed)

def test_amb_winner_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
    source_not_disposed = False
    o1 = scheduler.create_hot_observable(msgs1)
    
    def action():
        nonlocal source_not_disposed
        source_not_disposed = True
    
    o2 = scheduler.create_hot_observable(msgs2).do_action(on_next=action)
    
    def create():
        return o1.amb(o2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_error(220, ex))
    assert(not source_not_disposed)

def test_amb_loser_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(220, 2), on_error(230, ex)]
    msgs2 = [on_next(150, 1), on_next(210, 3), on_completed(250)]
    source_not_disposed = False
    
    def action():
        nonlocal source_not_disposed
        source_not_disposed = True
    o1 = scheduler.create_hot_observable(msgs1).do_action(on_next=action)
    
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return o1.amb(o2)
        
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 3), on_completed(250))
    assert(not source_not_disposed)

def test_amb_throws_before_election():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(210, ex)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(250)]
    source_not_disposed = False
    o1 = scheduler.create_hot_observable(msgs1)
    
    def action():
        nonlocal source_not_disposed
        source_not_disposed = True
    
    o2 = scheduler.create_hot_observable(msgs2).do_action(on_next=action)
    
    def create():
        return o1.amb(o2)
        
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(210, ex))
    assert(not source_not_disposed)

def test_catch_no_errors():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(230)]
    msgs2 = [on_next(240, 5), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return o1.catch_exception(o2)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_completed(230))

def test_catch_never():
    scheduler = TestScheduler()
    msgs2 = [on_next(240, 5), on_completed(250)]
    o1 = Observable.never()
    o2 = scheduler.create_hot_observable(msgs2)

    def create():
        return o1.catch_exception(o2)
    results = scheduler.start(create)
    
    results.messages.assert_equal()

def test_catch_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(240, 5), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return o1.catch_exception(o2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(230))

def test_catch_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    msgs2 = [on_next(240, 5), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)

    def create():
        return o1.catch_exception(o2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_completed(230))

def test_catch_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
    msgs2 = [on_next(240, 5), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return o1.catch_exception(o2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 5), on_completed(250))

def test_catch_error_never():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = Observable.never()
    def create():
        return o1.catch_exception(o2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3))

def test_catch_error_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, 'ex1')]
    msgs2 = [on_next(240, 4), on_error(250, ex)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return o1.catch_exception(o2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_error(250, ex))

def test_catch_multiple():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
    msgs2 = [on_next(220, 3), on_error(225, ex)]
    msgs3 = [on_next(230, 4), on_completed(235)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    o3 = scheduler.create_hot_observable(msgs3)
    
    def create():
        return Observable.catch_exception(o1, o2, o3)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(235))

def test_catch_error_specific_caught():
    ex = 'ex'
    handler_called = False
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
    msgs2 = [on_next(240, 4), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        def handler(e):
            nonlocal handler_called
            
            handler_called = True
            return o2

        return o1.catch_exception(handler)
    
    results = scheduler.start(create)

    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_completed(250))
    assert(handler_called)

def test_catch_error_specific_caught_immediate():
    ex = 'ex'
    handler_called = False
    scheduler = TestScheduler()
    msgs2 = [on_next(240, 4), on_completed(250)]
    o2 = scheduler.create_hot_observable(msgs2)

    def create():
        def handler(e):
            nonlocal handler_called
            handler_called = True
            return o2

        return Observable.throw_exception('ex').catch_exception(handler)

    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(240, 4), on_completed(250))
    assert(handler_called)

def test_catch_handler_throws():
    ex = 'ex'
    ex2 = 'ex2'
    handler_called = False
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, ex)]
    o1 = scheduler.create_hot_observable(msgs1)
    
    def create():
        def handler(e):
            nonlocal handler_called
            handler_called = True
            raise Exception(ex2)
        return o1.catch_exception(handler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_error(230, ex2))
    assert(handler_called)

def test_catch_nested_outer_catches():
    ex = 'ex'
    first_handler_called = False
    second_handler_called = False
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
    msgs2 = [on_next(220, 3), on_completed(225)]
    msgs3 = [on_next(220, 4), on_completed(225)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    o3 = scheduler.create_hot_observable(msgs3)
    
    def create():
        def handler1(e):
            nonlocal first_handler_called
            first_handler_called = True
            return o2
        def handler2(e):
            nonlocal second_handler_called
            second_handler_called = True
            return o3
        return o1.catch_exception(handler1).catch_exception(handler2)
    
    results = scheduler.start(create)    
    
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_completed(225))
    assert(first_handler_called)
    assert(not second_handler_called)

def test_catch_throw_from_nested_catch():
    ex = 'ex'
    ex2 = 'ex'
    first_handler_called = False
    second_handler_called = False
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(215, ex)]
    msgs2 = [on_next(220, 3), on_error(225, ex2)]
    msgs3 = [on_next(230, 4), on_completed(235)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    o3 = scheduler.create_hot_observable(msgs3)
    
    def create():
        def handler1(e):
            nonlocal first_handler_called
            first_handler_called = True
            assert(e == ex)
            return o2
        def handler2(e):
            nonlocal second_handler_called
            second_handler_called = True
            assert(e == ex2)
            return o3
        return o1.catch_exception(handler1).catch_exception(handler2)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(235))
    assert(first_handler_called)
    assert(second_handler_called)

def test_on_error_resume_next_no_errors():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(230)]
    msgs2 = [on_next(240, 4), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return o1.on_error_resume_next(o2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_completed(250))

def test_on_error_resume_next_Error():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_error(230, 'ex')]
    msgs2 = [on_next(240, 4), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return o1.on_error_resume_next(o2)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(240, 4), on_completed(250))

def test_on_error_resume_next_error_multiple():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, 'ex')]
    msgs2 = [on_next(230, 4), on_error(240, 'ex')]
    msgs3 = [on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    o3 = scheduler.create_hot_observable(msgs3)
    def create():
        return Observable.on_error_resume_next(o1, o2, o3)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, 2), on_next(230, 4), on_completed(250))

def test_on_error_resume_next_empty_return_throw_and_more():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(205)]
    msgs2 = [on_next(215, 2), on_completed(220)]
    msgs3 = [on_next(225, 3), on_next(230, 4), on_completed(235)]
    msgs4 = [on_error(240, 'ex')]
    msgs5 = [on_next(245, 5), on_completed(250)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    o3 = scheduler.create_hot_observable(msgs3)
    o4 = scheduler.create_hot_observable(msgs4)
    o5 = scheduler.create_hot_observable(msgs5)
    
    def create():
        return Observable.on_error_resume_next(o1, o2, o3, o4, o5)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(215, 2), on_next(225, 3), on_next(230, 4), on_next(245, 5), on_completed(250))

def test_on_error_resume_next_empty_return_throw_and_more():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(220)]
    msgs2 = [on_error(230, ex)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = scheduler.create_hot_observable(msgs2)
    def create():
        return o1.on_error_resume_next(o2)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, 2), on_completed(230))

def test_on_error_resume_next_single_source_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_error(230, ex)]
    o1 = scheduler.create_hot_observable(msgs1)
    def create():
        return Observable.on_error_resume_next(o1)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_completed(230))

def test_on_error_resume_next_end_with_never():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(220)]
    o1 = scheduler.create_hot_observable(msgs1)
    o2 = Observable.never()
    
    def create():
        return Observable.on_error_resume_next(o1, o2)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(210, 2))

def test_on_error_resume_next_start_with_never():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(220)]
    o1 = Observable.never()
    o2 = scheduler.create_hot_observable(msgs1)

    def create():
        return Observable.on_error_resume_next(o1, o2)

    results = scheduler.start(create)
    
    results.messages.assert_equal()

def test_zip_never_never():
    scheduler = TestScheduler()
    o1 = Observable.never()
    o2 = Observable.never()
    
    def create():
        return o1.zip(o2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_zip_never_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(210)]
    o1 = Observable.never()
    o2 = scheduler.create_hot_observable(msgs)

    def create():    
        return o1.zip(o2, lambda x, y: x + y)

    results = scheduler.start(create)    
    results.messages.assert_equal()

def test_zip_empty_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_completed(210)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():    
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(210))

def test_zip_empty_non_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():    
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(215))

def test_zip_non_empty_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(215))

def test_zip_never_non_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs)
    e2 = Observable.never()

    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_zip_non_empty_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs)
    e2 = Observable.never()

    def create():
        return e1.zip(e2, lambda x, y: x + y)
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_zip_non_empty_non_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2 + 3), on_completed(240))

def test_zip_empty_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_error_empty():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_never_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_error_never():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_error_error():
    ex1 = 'ex1'
    ex2 = 'ex2'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(230, ex1)]
    msgs2 = [on_next(150, 1), on_error(220, ex2)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex2))

def test_zip_some_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_error_some():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

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
#         assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == sum)
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
#         assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == sum)
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
#         assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == sum)
#     }
# 
def test_zip_selector_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(240)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_next(230, 5), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        def selector(x, y):
            if y == 5:
                raise Exception(ex)
            else:
                return x + y
            
        return e1.zip(e2, selector)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2 + 3), on_error(230, ex))

def test_combine_latest_never_never():
    scheduler = TestScheduler()
    e1 = Observable.never()
    e2 = Observable.never()

    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_never_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(210)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_empty_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(210)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_empty_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_completed(210)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)

    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(210))

def test_combine_latest_empty_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(215))

def test_combine_latest_return_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(215))

def test_combine_latest_never_feturn():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs)
    e2 = Observable.never()

    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_return_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(215, 2), on_completed(210)]
    e1 = scheduler.create_hot_observable(msgs)
    e2 = Observable.never()

    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_return_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2 + 3), on_completed(240))

def test_combine_latest_empty_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_error_empty():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_return_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_throw_return():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_throw_throw():
    ex1 = 'ex1'
    ex2 = 'ex2'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(220, ex1)]
    msgs2 = [on_next(150, 1), on_error(230, ex2)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex1))

def test_combine_latest_error_throw():
    ex1 = 'ex1'
    ex2 = 'ex2'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex1)]
    msgs2 = [on_next(150, 1), on_error(230, ex2)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create) 
    results.messages.assert_equal(on_error(220, ex1))

def test_combine_latest_throw_error():
    ex1 = 'ex1'
    ex2 = 'ex2'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex1)]
    msgs2 = [on_next(150, 1), on_error(230, ex2)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex1))

def test_combine_latest_never_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_error(220, ex)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

# def test_Combine_latest_ThrowNever():
#     var e1, e2, ex, msgs, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_error(220, ex)]
#     e1 = Observable.never()
#     e2 = scheduler.create_hot_observable(msgs)
#     results = scheduler.start(create)
#         return e2.combine_latest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Combine_latest_SomeThrow():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combine_latest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Combine_latest_ThrowSome():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_error(220, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.combine_latest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
# def test_Combine_latest_ThrowAfterCompleteLeft():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     msgs2 = [on_next(150, 1), on_error(230, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combine_latest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(230, ex))
# 
# def test_Combine_latest_ThrowAfterCompleteRight():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
#     msgs2 = [on_next(150, 1), on_error(230, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.combine_latest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(230, ex))
# 
# def test_Combine_latest_InterleavedWithTail():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_next(230, 5), on_next(235, 6), on_next(240, 7), on_completed(250)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combine_latest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(220, 2 + 3), on_next(225, 3 + 4), on_next(230, 4 + 5), on_next(235, 4 + 6), on_next(240, 4 + 7), on_completed(250))
# 
# def test_Combine_latest_Consecutive():
#     var e1, e2, msgs1, msgs2, results, scheduler
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_completed(250)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combine_latest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(235, 4 + 6), on_next(240, 4 + 7), on_completed(250))
# 
# def test_Combine_latest_ConsecutiveEndWithErrorLeft():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_error(230, ex)]
#     msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_completed(250)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combine_latest(e2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(230, ex))
# 
# def test_Combine_latest_ConsecutiveEndWithErrorRight():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_error(245, ex)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e2.combine_latest(e1, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(235, 4 + 6), on_next(240, 4 + 7), on_error(245, ex))
# 
# def test_Combine_latest_SelectorThrows():
#     var e1, e2, ex, msgs1, msgs2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
#     msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
#     e1 = scheduler.create_hot_observable(msgs1)
#     e2 = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create)
#         return e1.combine_latest(e2, function () {
#             throw ex
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
# 
def test_concat_empty_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(250))

def test_concat_empty_never():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = Observable.never()
    
    def create():
        return e1.concat(e2)
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_concat_never_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = Observable.never()
    def create():
        return e2.concat(e1)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_Concat_NeverNever():
    scheduler = TestScheduler()
    e1 = Observable.never()
    e2 = Observable.never()
    
    def create():
        return e1.concat(e2)
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_Concat_EmptyThrow():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(250, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(250, ex))

def test_concat_throw_empty():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(230, ex)]
    msgs2 = [on_next(150, 1), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(230, ex))

def test_concat_throw_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(230, ex)]
    msgs2 = [on_next(150, 1), on_error(250, 'ex2')]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.concat(e2)
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(230, ex))

def test_concat_return_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.concat(e2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_completed(250))

def test_concat_empty_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(240, 2), on_completed(250))

def test_concat_return_never():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = Observable.never()
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2))

def test_concat_never_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = Observable.never()
    
    def create():
        return e2.concat(e1)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_concat_return_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(240, 3), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2), on_next(240, 3), on_completed(250))

def test_Concat_ThrowReturn():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(230, ex)]
    msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_error(230, ex))

def test_concat_return_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(250, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.concat(e2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2), on_error(250, ex))

def test_concat_some_data_some_data():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(225)]
    msgs2 = [on_next(150, 1), on_next(230, 4), on_next(240, 5), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.concat(e2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

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
# def test_ZipWithEnumerable_NeverEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1))
#     n2 = []
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
#     n1.subscriptions.assert_equal(subscribe(200, 1000))
# 
# def test_ZipWithEnumerable_EmptyEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210))
#     n2 = []
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(210))
#     n1.subscriptions.assert_equal(subscribe(200, 210))
# 
# def test_ZipWithEnumerable_EmptyNonEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210))
#     n2 = [2]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(210))
#     n1.subscriptions.assert_equal(subscribe(200, 210))
# 
# def test_ZipWithEnumerable_NonEmptyEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_completed(220))
#     n2 = []
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(215))
#     n1.subscriptions.assert_equal(subscribe(200, 215))
# 
# def test_ZipWithEnumerable_NeverNonEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1))
#     n2 = [2]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
#     n1.subscriptions.assert_equal(subscribe(200, 1000))
# 
# def test_ZipWithEnumerable_NonEmptyNonEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_completed(230))
#     n2 = [3]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(215, 2 + 3), on_completed(230))
#     n1.subscriptions.assert_equal(subscribe(200, 230))
# 
# def test_ZipWithEnumerable_ErrorEmpty():
#     var ex, n1, n2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex))
#     n2 = []
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
#     n1.subscriptions.assert_equal(subscribe(200, 220))
# 

# def test_ZipWithEnumerable_ErrorSome():
#     var ex, n1, n2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex))
#     n2 = [2]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
#     n1.subscriptions.assert_equal(subscribe(200, 220))
# 
# def test_ZipWithEnumerable_SomeDataBothSides():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5))
#     n2 = [5, 4, 3, 2]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(210, 7), on_next(220, 7), on_next(230, 7), on_next(240, 7))
#     n1.subscriptions.assert_equal(subscribe(200, 1000))
# 
# def test_ZipWithEnumerable_SelectorThrows():
#     var ex, n1, n2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(240))
#     n2 = [3, 5]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             if (y == 5) {
#                 throw ex
#             }
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(215, 2 + 3), on_error(225, ex))
#     n1.subscriptions.assert_equal(subscribe(200, 225))
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
    test_zip_empty_non_empty()