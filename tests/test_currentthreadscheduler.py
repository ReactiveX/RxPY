from datetime import datetime, timedelta

from rx.concurrency import Scheduler, CurrentThreadScheduler

def test_currentthread_now():
    res = Scheduler.now() - datetime.utcnow()
    assert res < timedelta(milliseconds=1000)

def test_currentthread_scheduleaction():
    scheduler = CurrentThreadScheduler()
    ran = False

    def action(scheduler, state=None):
        nonlocal ran
        ran = True

    scheduler.schedule(action)
    assert ran == True

def test_currentthread_scheduleactionerror():
    scheduler = CurrentThreadScheduler()

    class MyException(Exception):
        pass

    def action(scheduler, state=None):
        raise MyException()
        
    try:
        return scheduler.schedule(action)
    except MyException:
        assert True

def test_currentthread_scheduleactionnested():
    scheduler = CurrentThreadScheduler()
    ran = False
    
    def action(scheduler, state=None):
        def inner_action(scheduler, state=None):
            nonlocal ran
            ran = True

        return scheduler.schedule(inner_action)
    scheduler.schedule(action)
    
    assert ran == True

def test_currentthread_ensuretrampoline():
    scheduler = CurrentThreadScheduler()
    ran1, ran2 = False, False
    
    def outer_action(scheduer, state=None):
        def action1(scheduler, state=None):
            nonlocal ran1
            ran1 = True

        scheduler.schedule(action1)

        def action2(scheduler, state=None):
            nonlocal ran2
            ran2 = True

        return scheduler.schedule(action2)

    scheduler.ensure_trampoline(outer_action)
    assert ran1 == True
    assert ran2 == True

def test_currentthread_ensuretrampoline_nested():
    scheduler = CurrentThreadScheduler()
    ran1, ran2 = False, False

    def outer_action(scheduler, state):
        def inner_action1(scheduler, state):
            nonlocal ran1
            ran1 = True
        
        scheduler.ensure_trampoline(inner_action1)
        
        def inner_action2(scheduler, state):
            nonlocal ran2
            ran2 = True
        
        return scheduler.ensure_trampoline(inner_action2)

    scheduler.ensure_trampoline(outer_action)
    assert ran1 == True
    assert ran2 == True

def test_currentthread_ensuretrampoline_and_cancel():
    scheduler = CurrentThreadScheduler()
    ran1, ran2 = False, False

    def outer_action(scheduler, state):
        def inner_action1(scheduler, state):
            nonlocal ran1
            ran1 = True

            def inner_action2(scheduler, state):
                nonlocal ran2
                ran2 = True

            d = scheduler.schedule(inner_action2)
            d.dispose()

        return scheduler.schedule(inner_action1)

    scheduler.ensure_trampoline(outer_action)
    assert ran1 == True
    assert ran2 == False

def test_currentthread_ensuretrampoline_and_canceltimed():
    scheduler = CurrentThreadScheduler()
    ran1, ran2 = False, False
    
    def outer_action(scheduler, state):
        def inner_action1(scheduler, state):
            nonlocal ran1
            ran1 = True

            def inner_action2(scheduler, state):
                nonlocal ran2
                ran2 = True

            d = scheduler.schedule_relative(timedelta(milliseconds=500), inner_action2)
            d.dispose()

        return scheduler.schedule(inner_action1)

    scheduler.ensure_trampoline(outer_action)
    assert ran1 == True
    assert ran2 == False
