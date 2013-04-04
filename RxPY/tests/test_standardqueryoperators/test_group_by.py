import math
from datetime import datetime

from rx.observable import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

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

def test_group_by_with_key_comparer():
    scheduler = TestScheduler()
    key_invoked = 0
    xs = scheduler.create_hot_observable(
                        on_next(90, "error"),
                        on_next(110, "error"),
                        on_next(130, "error"),
                        on_next(220, "  foo"),
                        on_next(240, " FoO "),
                        on_next(270, "baR  "),
                        on_next(310, "foO "),
                        on_next(350, " Baz   "),
                        on_next(360, "  qux "),
                        on_next(390, "   bar"),
                        on_next(420, " BAR  "),
                        on_next(470, "FOO "),
                        on_next(480, "baz  "),
                        on_next(510, " bAZ "),
                        on_next(530, "    fOo    "),
                        on_completed(570),
                        on_next(580, "error"),
                        on_completed(600),
                        on_error(650, 'ex'))

    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()
        
        return xs.group_by(key_selector, lambda x: x).select(lambda g: g.key)
        
    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_completed(570))
    xs.subscriptions.assert_equal(subscribe(200, 570))
    assert(key_invoked == 12)

def test_groupby_outer_complete():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    
    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()

        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            return x[::-1] # Yes, this is reverse string in Python

        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_completed(570))
    xs.subscriptions.assert_equal(subscribe(200, 570))
    assert(key_invoked == 12)
    assert(ele_invoked == 12)

def test_group_by_outer_error():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_error(570, ex), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    
    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()
        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            return x[::-1]
        
        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)

    results = scheduler.start_with_create(factory)

    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_error(570, ex))
    xs.subscriptions.assert_equal(subscribe(200, 570))
    assert(key_invoked == 12)
    assert(ele_invoked == 12)


def test_group_by_outer_dispose():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    
    def dispose():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()
        
        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            return x[::-1]

        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)

    results = scheduler.start_with_dispose(dispose, 355)
    
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"))
    xs.subscriptions.assert_equal(subscribe(200, 355))
    assert(key_invoked == 5)
    assert(ele_invoked == 5)

def test_group_by_outer_key_throw():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            if key_invoked == 10:
                raise Exception(ex)
            
            return x.lower().strip()

        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            return x[::-1]
        
        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)
     
    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_error(480, ex))
    xs.subscriptions.assert_equal(subscribe(200, 480))
    assert(key_invoked == 10)
    assert(ele_invoked == 9)

def test_group_by_outer_ele_throw():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    
    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()
        
        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            if ele_invoked == 10:
                raise Exception(ex)
            return x[::-1]

        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_error(480, ex))
    xs.subscriptions.assert_equal(subscribe(200, 480))
    assert(key_invoked == 10)
    assert(ele_invoked == 10)

def test_group_by_inner_complete():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    outer_subscription = None
    inner_subscriptions = {}
    inners = {}
    results = {}
    outer = None

    def action1(scheduler, state):
        nonlocal outer
        outer = xs.group_by(lambda x: x.lower().strip(), lambda x: x[::-1])
    
    scheduler.schedule_absolute(created, action1)
    
    def action2(scheduler, state):
        nonlocal outer_subscription

        def next(group):
            nonlocal results, inners

            result = scheduler.create_observer()
            inners[group.key] = group
            results[group.key] = result

            def action21(scheduler, state):
                nonlocal inner_subscriptions
                inner_subscriptions[group.key] = group.subscribe(result)

            scheduler.schedule_relative(100, action21)
        outer_subscription = outer.subscribe(next)
    scheduler.schedule_absolute(subscribed, action2)
    
    def action3(scheduler, state):
        outer_subscription.dispose()
        for sub in inner_subscriptions.values():
            sub.dispose()
        
    scheduler.schedule_absolute(disposed, action3)
    scheduler.start()
    assert(len(inners) == 4)
    results['foo'].messages.assert_equal(on_next(470, " OOF"), on_next(530, "    oOf    "), on_completed(570))
    results['bar'].messages.assert_equal(on_next(390, "rab   "), on_next(420, "  RAB "), on_completed(570))
    results['baz'].messages.assert_equal(on_next(480, "  zab"), on_next(510, " ZAb "), on_completed(570))
    results['qux'].messages.assert_equal(on_completed(570))
    xs.subscriptions.assert_equal(subscribe(200, 570))

def test_group_by_inner_complete_all():
    #var innerSubscriptions, inners, outer, outerSubscription, results, scheduler, xs;
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    outer = None
    outer_subscription = None
    inners = {}
    inner_subscriptions = {}
    results = {}
    result = None

    def action1(scheduler, state):
        nonlocal outer
        outer = xs.group_by(
            lambda x: x.lower().strip(), 
            lambda x: x[::-1]
        )
        return outer
    scheduler.schedule_absolute(created, action1)

    def action2(scheduler, state):
        nonlocal outer_subscription

        def on_next(group):
            nonlocal result, inners, results, inner_subscriptions
            result = scheduler.create_observer()
            inners[group.key] = group
            results[group.key] = result
            inner_subscriptions[group.key] = group.subscribe(result)
        outer_subscription = outer.subscribe(on_next)
        return outer_subscription
    scheduler.schedule_absolute(subscribed, action2)

    def action3(scheduler, state):
        outer_subscription.dispose()
        for sub in inner_subscriptions.values():
            sub.dispose()
    scheduler.schedule_absolute(disposed, action3)
        
    scheduler.start()
    assert(len(inners) == 4)
    results['foo'].messages.assert_equal(on_next(220, "oof  "), on_next(240, " OoF "), on_next(310, " Oof"), on_next(470, " OOF"), on_next(530, "    oOf    "), on_completed(570))
    results['bar'].messages.assert_equal(on_next(270, "  Rab"), on_next(390, "rab   "), on_next(420, "  RAB "), on_completed(570))
    results['baz'].messages.assert_equal(on_next(350, "   zaB "), on_next(480, "  zab"), on_next(510, " ZAb "), on_completed(570))
    results['qux'].messages.assert_equal(on_next(360, " xuq  "), on_completed(570))
    xs.subscriptions.assert_equal(subscribe(200, 570))

def test_group_by_inner_error():
    ex = 'ex1'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_error(570, ex), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    outer_subscription = None
    inner_subscriptions = {}
    inners = {}
    outer = None
    results = {}
    result = None

    def action1(scheduler, state):
        nonlocal outer
        outer = xs.group_by(
            lambda x: x.lower().strip(), 
            lambda x: x[::-1]
        )
        return outer
    scheduler.schedule_absolute(created, action1)

    def action2(scheduler, state):
        nonlocal outer_subscription

        def on_next(group):
            nonlocal result, inners, results

            result = scheduler.create_observer()
            inners[group.key] = group
            results[group.key] = result

            def action3(scheduler, state):
                nonlocal inner_subscriptions
                inner_subscriptions[group.key] = group.subscribe(result)
            
            scheduler.schedule_relative(100, action3)
        outer_subscription = outer.subscribe(on_next, lambda e: None)
        return outer_subscription
    scheduler.schedule_absolute(subscribed, action2)

    def action4(scheduler, state):
        outer_subscription.dispose();
        for sub in inner_subscriptions.values():
            sub.dispose()
    scheduler.schedule_absolute(disposed, action4)

    scheduler.start()
    assert(len(inners) == 4)
    #results['foo'].messages.assert_equal(on_next(470, " OOF"), on_next(530, "    oOf    "), on_error(570, ex))
    #results['bar'].messages.assert_equal(on_next(390, "rab   "), on_next(420, "  RAB "), on_error(570, ex))
    #results['baz'].messages.assert_equal(on_next(480, "  zab"), on_next(510, " ZAb "), on_error(570, ex))
    #results['qux'].messages.assert_equal(on_error(570, ex))
    xs.subscriptions.assert_equal(subscribe(200, 570))


if __name__ == '__main__':
    test_group_by_inner_error()
