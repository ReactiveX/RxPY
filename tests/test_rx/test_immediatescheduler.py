from datetime import datetime, timedelta

from rx.concurrency import Scheduler, ImmediateScheduler
from rx.disposables import DisposableEmpty

def test_immediate_now():
    res = Scheduler.now() - datetime.utcnow()
    assert res < timedelta(milliseconds=1000)

def test_immediate_scheduleaction():
    scheduler = ImmediateScheduler()
    ran = False;

    def action(scheduler, state=None):
        nonlocal ran
        ran = True

    scheduler.schedule(action)
    assert ran

def test_immediate_scheduleactionerror():
    scheduler = ImmediateScheduler()

    class MyException(Exception):
        pass

    def action(scheduler, state=None):
        raise MyException()
        
    try:
        return scheduler.schedule(action)
    except MyException:
        assert True

def test_immediate_simple1():
    scheduler = ImmediateScheduler()
    xx = 0

    def action(scheduler, state=None):
        nonlocal xx
        xx = state
        return DisposableEmpty()

    scheduler.schedule(action, 42)
    assert xx == 42

def test_immediate_simple2():
    scheduler = ImmediateScheduler()
    xx = 0
    
    def action(scheduler, state=None):
         nonlocal xx
         xx = state
         return DisposableEmpty()

    scheduler.schedule_absolute(datetime.utcnow(), action, 42);
    assert xx == 42

def test_immediate_simple3():
    scheduler = ImmediateScheduler()
    xx = 0
    
    def action(scheduler, state=None):
         nonlocal xx
         xx = state
         return DisposableEmpty()

    scheduler.schedule_relative(timedelta(0), action, 42);
    assert xx == 42

def test_immediate_recursive1():
    scheduler = ImmediateScheduler()
    xx = 0
    yy = 0
    
    def action(scheduler, x=None):
        nonlocal xx
        
        xx = x
        
        def inner_action(scheduler, y):
            nonlocal yy
            yy = y
            return DisposableEmpty()
        
        return scheduler.schedule(inner_action, 43) 

    scheduler.schedule(action, 42)
    assert xx == 42
    assert yy == 43

def test_immediate_recursive2():
    scheduler = ImmediateScheduler()
    xx = 0
    yy = 0
    
    def action(scheduler, state=None):
        nonlocal xx
        xx = state
        
        def inner_action(scheduler, state=None):
            nonlocal yy
            yy = state
            return DisposableEmpty

        return scheduler.schedule_absolute(datetime.utcnow(), inner_action, 43)

    scheduler.schedule_absolute(datetime.utcnow(), action, 42) 

    assert xx == 42
    assert yy == 43

def test_immediate_recursive3():
    scheduler = ImmediateScheduler()
    xx = 0
    yy = 0

    def action(scheduler, state=None):
        nonlocal xx
        xx = state

        def inner_action(scheduler, state):
            nonlocal yy
            yy = state
            return DisposableEmpty()

        return scheduler.schedule_relative(timedelta(0), inner_action, 43)
    
    scheduler.schedule_relative(timedelta(0), action, 42) 
    
    
    assert xx == 42
    assert yy == 43
